from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash, session
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Table
from .models import DVRPSet, DVRPOrigin, GeoPoints, db
# from . import db
import openrouteservice
import os


views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = set(['csv'])


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method =='POST':
        file = request.files['file']
        origin = request.form.get('origin')
        if file and allowed_file(file.filename):
            try:
                df = pd.read_csv(file, header=None)
                dist_v = df[0].unique()
                sequence_v = df[4].unique()
                dist_db_v = db.session.query(DVRPSet.dvrp_id).distinct().all()
                dist_db_v = [i[0] for i in dist_db_v]
                print(sequence_v)
                if (dist_v in dist_db_v) or (pd.isna(sequence_v).any()):
                    if dist_v in dist_db_v:
                        message = 'dvrp_id exists in dvrp_set table'
                        flash(message, category='error')
                    if pd.isna(sequence_v).any():
                        message = 'sequence contains null'
                        flash(message, category='error')
                else:
                    for index, row in df.iterrows():
                        dvrp_set = DVRPSet(
                            dvrp_id=row[0],
                            cluster_id=int(row[1]),
                            cluster_name=row[2],
                            point=row[3],
                            sequence=row[4]
                        )
                        db.session.add(dvrp_set)

                    dist_v_arr = [x for x in dist_v]
                    origin_arr = [origin for x in dist_v]
                    for dvrp_id, dvrp_origin in zip(dist_v_arr, origin_arr):
                        dvrp_origin_entry = DVRPOrigin(
                            dvrp_id=dvrp_id,
                            dvrp_origin=dvrp_origin
                        )
                        db.session.add(dvrp_origin_entry)

                    db.session.commit()
                    message = 'set added to dvrp_set table'
                    flash(message, category='success')
            except Exception as e:
                db.session.rollback()

    dvrp_sets = db.session.query(
        DVRPOrigin.dvrp_id, DVRPOrigin.dvrp_origin
    ).join(
        DVRPSet, DVRPOrigin.dvrp_id == DVRPSet.dvrp_id
    ).distinct().all()

    return render_template('home.html', dvrp_sets=dvrp_sets)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/plot-table')
def plot_table():
    dvrp_id = request.args.get('dvrpId')
    if dvrp_id is not None:
        # If a specific DVRP ID is provided, filter the query
        dvrp_set_query = DVRPSet.query.filter_by(dvrp_id=dvrp_id)
    else:
        # Otherwise, fetch all records
        dvrp_set_query = DVRPSet.query

    dvrp_set_all = dvrp_set_query.all()
    dvrp_set_all_data = [
        {column.name: getattr(row, column.name) for column in row.__table__.columns}
        for row in dvrp_set_all
    ]
    dvrp_set_all_data = [
        {column.name: getattr(row, column.name) for column in row.__table__.columns} 
        for row in dvrp_set_all
    ]
    df_dvrp_set_all = pd.DataFrame(dvrp_set_all_data)

    fig_dvrp_set_all = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_dvrp_set_all.columns),
            fill_color='paleturquoise',
            align='left'
        ),
        cells=dict(
            values=[df_dvrp_set_all[col].tolist() for col in df_dvrp_set_all.columns],
            fill_color='lavender',
            align='left'
        )
    )])

    fig_dvrp_set_all.update_layout(
        margin=dict(l=10, r=18, t=28, b=10)
    )

    return jsonify(fig_dvrp_set_all.to_dict())


@views.route('/map-data')
def map_data():
    dvrp_id = request.args.get('dvrpId')
    ors_api_key = os.getenv('ORS_API_KEY')
    client = openrouteservice.Client(key=ors_api_key)

    if dvrp_id:
        clusters_points = fetch_clusters_points(dvrp_id)
        
        # Initialize an empty figure with a Mapbox layout
        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            text=[],  # Empty text list, you can populate it based on your needs
            marker={'size': 9}))
        fig.update_layout(
            mapbox={
                'style': "open-street-map",
                'zoom': 10  # Adjust the zoom level according to your preference
            },
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
        )
        
        # Iterate over your cluster points here to add them to the figure
        # For each cluster, you might need to get the route from OpenRouteService as before,
        # then plot the route and markers using fig.add_trace() methods.
        
        # Example of adding a single route (you should replace this with your actual loop over clusters_points):
        # This is a placeholder loop. Replace with actual data processing.
        for cluster_id, coords in clusters_points.items():
            route = client.directions(coords, profile='driving-hgv', format='geojson')
            line_coords = route['features'][0]['geometry']['coordinates']
            fig.add_trace(go.Scattermapbox(
                lon=[c[0] for c in line_coords],
                lat=[c[1] for c in line_coords],
                mode='lines',
                line=dict(width=4, color='blue'),  # Adjust color dynamically if needed
                hoverinfo='none'
            ))
            # Add markers or other customizations as needed

        # Serialize figure to JSON for response
        return jsonify(fig.to_dict())

    return jsonify(error="dvrpId not specified"), 400


def fetch_clusters_points(dvrp_id):
    # Dictionary to hold the clusters and their points
    clusters_points = {}

    # Query the database for all points associated with the dvrp_id, sorted by cluster_id and sequence
    points_query = db.session.query(DVRPSet.cluster_id, GeoPoints.coordinates)\
                     .join(GeoPoints, DVRPSet.point == GeoPoints.id)\
                     .filter(DVRPSet.dvrp_id == dvrp_id)\
                     .order_by(DVRPSet.cluster_id, DVRPSet.sequence)\
                     .all()

    # Origin point, assuming it's associated with each cluster_id but not stored as part of the DVRPSet
    origin_query = GeoPoints.query.filter_by(id='way/701209222').first()
    if origin_query:
        origin_coords = json.loads(origin_query.coordinates)
    else:
        # Handle case where origin is not found
        origin_coords = None

    # Iterate over the query results and populate the clusters_points dictionary
    for cluster_id, coordinates in points_query:
        if cluster_id not in clusters_points:
            clusters_points[cluster_id] = [origin_coords] if origin_coords else []
        
        # Append the point's coordinates, converting from string to list
        clusters_points[cluster_id].append(json.loads(coordinates))

        # Ensure the origin is also the last point in the route
        if origin_coords:
            clusters_points[cluster_id].append(origin_coords)

    return clusters_points


# @views.route('/map-data')
# def map_data():
#     # Use os.getenv to get the environment variable value
#     ors_api_key = os.getenv('ORS_API_KEY')
#     client = openrouteservice.Client(key=ors_api_key)

#     # Define coordinates of the points (lon, lat)
#     coords = ((-73.935242, 40.730610), (-73.969262, 40.751990))

#     # Request route between the points
#     routes = client.directions(coords, profile='driving-hgv', format='geojson')
    
#     # Plot the route using Plotly
#     fig = px.line_mapbox(lon=[pt[0] for pt in routes['features'][0]['geometry']['coordinates']],
#                          lat=[pt[1] for pt in routes['features'][0]['geometry']['coordinates']],
#                          mapbox_style="open-street-map", zoom=10)

#     # Optionally, add the points as markers on top of the route, adjusting the size here
#     fig.add_trace(px.scatter_mapbox(lat=[40.730610, 40.751990], lon=[-73.935242, -73.969262], size_max=15, size=[15]*len([40.730610, 40.751990])).data[0])
    
#     fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

#     return jsonify(fig=fig.to_json())