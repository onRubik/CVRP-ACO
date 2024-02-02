from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash, session
from .clustering import ClusteringService
from .tsp import TspService
from .load_points import load_points  
from .vrp import vrp  
import pandas as pd
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
                    # print('it went in')
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
                    db.session.commit()

                    dist_v_arr = [x for x in dist_v]
                    origin_arr = ['DC10' for x in dist_v]
                    print(dist_v_arr)
                    print(origin_arr)

                    dvrp_origin = DVRPOrigin(
                        dvrp_id=dist_v_arr,
                        dvrp_origin=origin_arr
                    )
                    db.session.add(dvrp_origin)

                    db.session.commit()
                    message = 'set added to dvrp_set table'
                    flash(message, category='success')
            except Exception as e:
                db.session.rollback()

    dvrp_sets = db.session.query(
        DVRPOrigin.dvrp_id, DVRPOrigin.dvrp_origin, DVRPSet.point
    ).join(
        DVRPSet, DVRPOrigin.dvrp_id == DVRPSet.dvrp_id
    ).distinct().all()

    return render_template('home.html', dvrp_sets=dvrp_sets)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS