from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from . import auth
from ..models import User
from .. import get_db

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_username(username)
        if user:
            flash('Username already exists')
        else:
            db = get_db()
            db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, generate_password_hash(password)))
            db.commit()
            new_user = User.get_by_username(username)
            login_user(new_user)
            return redirect(url_for('main.dashboard'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
