from flask import render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_required, current_user
from .clustering import ClusteringService
from .tsp import TspService
from .load_points import load_points  
from .vrp import vrp  
import pandas as pd


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        file = request.files['file']
        origin = request.form['origin']
        max_pallets = int(request.form['max_pallets'])
        max_pounds = float(request.form['max_pounds'])

        if 'process_cluster' in request.form:
            clusters = process_csv(file, ClusteringService.cluster_nearest_node, origin, max_pallets, max_pounds)
            if clusters is not None:
                return render_template('cluster_result.html', clusters=clusters)
            else:
                flash('Error processing clustering', category='error')

        elif 'process_tsp' in request.form:
            tsp_result = process_csv(file, TspService.tsp_service, origin, max_pallets, max_pounds)
            if tsp_result is not None:
                return render_template('tsp_result.html', tsp_result=tsp_result)
            else:
                flash('Error processing TSP', category='error')

        elif 'process_vrp' in request.form:
            vrp_result = process_csv(file, vrp, origin, max_pallets, max_pounds)
            if vrp_result is not None:
                return render_template('vrp_result.html', vrp_result=vrp_result)
            else:
                flash('Error processing VRP', category='error')

    return render_template('home.html', user=current_user)


def process_csv(file, processing_function, *args):
    if file.filename == '':
        return redirect(url_for('views.home'))
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        flash('Empty CSV file', category='error')
        return redirect(url_for('views.home'))
    except pd.errors.ParserError:
        flash('Invalid CSV file', category='error')
        return redirect(url_for('views.home'))

    if 'id' in df.columns:
        selected_columns = ['id']
        points = df[selected_columns].values.tolist()
    else:
        flash('CSV file must contain an "id" column', category='error')
        return redirect(url_for('views.home'))

    return processing_function(points, *args)