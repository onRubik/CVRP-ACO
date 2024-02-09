from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash, session
from .clustering import ClusteringService
from .tsp import TspService
from .load_points import load_points  
from .vrp import vrp  
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Table
from .models import DVRPSet, DVRPOrigin
from . import db


views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = set(['csv'])


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method =='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                df = pd.read_csv(file, header=None)
                dist_v = df[0].unique()
                dist_db_v = db.session.query(DVRPSet.dvrp_id).distinct().all()
                dist_db_v = [i[0] for i in dist_db_v]
                if dist_v in dist_db_v:
                    message = 'dvrp_id exists in dvrp_set table'
                    flash(message, category='error')
                else:
                    for index, row in df.iterrows():
                        dvrp_set = DVRPSet(
                            dvrp_id=row[0],
                            cluster_id=int(row[1]),
                            cluster_name=row[2],
                            point=row[3]
                        )
                        db.session.add(dvrp_set)

                    dist_v_arr = [x for x in dist_v]
                    origin_arr = ['DC10' for x in dist_v]
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


@views.route('/plot-table')
def plot_table():
    dvrp_set_all = db.session.query(DVRPSet).all()
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

    return jsonify(fig_dvrp_set_all.to_dict())


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS