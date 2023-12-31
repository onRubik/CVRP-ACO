from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
# from .models import Note
from . import db
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    return render_template("home.html", user=current_user)


@views.route('/attach-file', methods=['POST'])
def attach_file():  

    return render_template("home.html", user=current_user)