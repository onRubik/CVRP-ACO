from flask import render_template, request, Blueprint, jsonify, flash, has_request_context
import pandas as pd
import json
from ast import literal_eval
import plotly.graph_objects as go
from .models import DVRPSet, DVRPOrigin, GeoPoints, db
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
        # dvrp_set_query = DVRPSet.query.filter_by(dvrp_id=dvrp_id, id_set=id_set)
        dvrp_set_query = DVRPSet.query.filter_by(dvrp_id=dvrp_id)
        # dvrp_set_query = DVRPSet.query
    else:
        # Otherwise, fetch all records
        dvrp_set_query = DVRPSet.query

    dvrp_set_all = dvrp_set_query.all()
    dvrp_set_all_data = [
        {column.name: getattr(row, column.name) for column in row.__table__.columns}
        for row in dvrp_set_all
    ]
    # dvrp_set_all_data = [
    #     {column.name: getattr(row, column.name) for column in row.__table__.columns} 
    #     for row in dvrp_set_all
    # ]
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

    origin_node = db.session.query(DVRPOrigin.dvrp_origin)\
                    .filter(DVRPOrigin.dvrp_id == dvrp_id)\
                    .first()

    origin_node_coords = db.session.query(GeoPoints.lat, GeoPoints.lon)\
                    .filter(GeoPoints.id_p == origin_node.dvrp_origin)\
                    .first()

    origin_lat, origin_lon = origin_node_coords
    origin_node_coords_list = [float(origin_lon), float(origin_lat)]

    if dvrp_id:
        clusters_points = fetch_clusters_points(dvrp_id)
        
        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            text=[],
            marker={'size': 15}))
        fig.update_layout(
            mapbox={
                'style': "open-street-map",
                # 'style': "mapbox://styles/mapbox/streets-v11",  # Using a predefined Mapbox style
                'zoom': 10,
                'center': dict(lat=origin_lat, lon=origin_lon),
            },
            margin={'l': 0, 'r': 0, 't': 30, 'b': 0}
        )

        for cluster_id, coords in clusters_points.items():
            coords_list = [origin_node_coords_list] + [item['coords'] for item in coords] + [origin_node_coords_list]
            route = client.directions(coords_list, profile='driving-hgv', format='geojson')
            line_coords = route['features'][0]['geometry']['coordinates']
            fig.add_trace(go.Scattermapbox(
                lon=[c[0] for c in line_coords],
                lat=[c[1] for c in line_coords],
                mode='lines',
                hoverinfo='none',
                line={'width': 4},
                name=f"Cluster {cluster_id}",
            ))

            for point in coords:
                point_text = str(point['sequence']) +' > '+point['desc']
                fig.add_trace(go.Scattermapbox(
                    lon=[point['coords'][0]],
                    lat=[point['coords'][1]],
                    marker={'size': 16, 'color': 'gray'},
                    text=[point_text],
                    mode='markers',
                    hoverinfo='text',
                    name=f"Cluster {cluster_id} Point {point['sequence']}",
                    # legendgroup=f"cluster{cluster_id}",
                ))

        fig.add_trace(go.Scattermapbox(
            mode='markers',
            lon=[origin_lon],
            lat=[origin_lat],
            marker={'size': 20, 'color': 'red'},
            name='Origin',
        ))

        return jsonify(fig.to_dict())

    return jsonify(error="dvrpId not specified"), 400


def fetch_clusters_points(dvrp_id):
    clusters_points = {}

    points_query = db.session.query(
        DVRPSet.cluster_id, DVRPSet.sequence, GeoPoints.lat, GeoPoints.lon, DVRPSet.point
    ).join(
        GeoPoints, DVRPSet.point == GeoPoints.id_p
    ).filter(
        DVRPSet.dvrp_id == dvrp_id
    ).order_by(
        DVRPSet.cluster_id, DVRPSet.sequence
    ).all()

    for cluster_id, sequence, lat, lon, point_description in points_query:
        coordinates = f"[{lon}, {lat}]"
        if cluster_id not in clusters_points:
            clusters_points[cluster_id] = []

        clusters_points[cluster_id].append({
            'coords': json.loads(coordinates),
            'sequence': sequence,
            'desc': point_description
        })

    return clusters_points