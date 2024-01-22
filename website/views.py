from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from flask_login import login_required, current_user
from .clustering import ClusteringService
from .tsp import TspService
from .load_points import load_points  
from .vrp import vrp  
import pandas as pd
from .models import DVRPSet, DVRPOrigin
from . import db
# from werkzeug.utils import secure_filename
# from datetime import datetime


views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = set(['csv'])


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method =='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                df = pd.read_csv(file, header=None)
                dist_v = df[0].unique()
                dist_db_v = db.session.query(DVRPSet.dvrp_id).distinct().all()
                print(dist_db_v)
                dist_db_v = [i[0] for i in dist_db_v]
                if dist_v in dist_db_v:
                    error_message = 'dvrp_id exists in dvrp_set table'
                    return jsonify({'message': error_message, 'type': 'error'})

                for index, row in df.iterrows():
                    dvrp_set = DVRPSet(
                        dvrp_id=row[0],
                        cluster_id=int(row[1]),
                        cluster_name=row[2],
                        point=row[3]
                    )
                    db.session.add(dvrp_set)

                db.session.commit()
                # flash('File uploaded successfully', 'success')
            except Exception as e:
                db.session.rollback()
                # flash(f'Error uploading file: {str(e)}', 'error')

    dvrp_sets = db.session.query(
        DVRPOrigin.dvrp_id, DVRPOrigin.dvrp_origin, DVRPSet.point
    ).join(
        DVRPSet, DVRPOrigin.dvrp_id == DVRPSet.dvrp_id
    ).distinct().all()

    return render_template('home.html', user=current_user, dvrp_sets=dvrp_sets)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS