from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('floatingInput')
        password = request.form.get('floatingPassword')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                message = 'Logged in successfully!'
                login_user(user, remember=True)
                return jsonify({'message': message, 'type': 'success'})
            else:
                message = 'Incorrect password, try again.'
                return jsonify({'message': message, 'type': 'error'})
        else:
            message = 'Email does not exist.'
            return jsonify({'message': message, 'type': 'error'})
    
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('floatingInput')
        first_name = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            # flash('Email already exists.', category='error')
            print('Email already exists.')
            return redirect(url_for('auth.sign_up'))
        elif len(email) < 4:
            # flash('Email must be greater than 3 characters.', category='error')
            print('Email must be greater than 3 characters.')
            return redirect(url_for('auth.sign_up'))
        elif len(first_name) < 2:
            # flash('First name must be greater than 1 character.', category='error')
            print('First name must be greater than 1 character.')
            return redirect(url_for('auth.sign_up'))
        elif password1 != password2:
            # flash('Passwords don\'t match.', category='error')
            print('Passwords don\'t match.')
            return redirect(url_for('auth.sign_up'))
        elif len(password1) < 7:
            # flash('Password must be at least 7 characters.', category='error')
            print('Password must be at least 7 characters.')
            return redirect(url_for('auth.sign_up'))
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            # flash('Account created!', category='success')
            print('Account created!')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)