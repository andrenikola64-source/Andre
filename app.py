from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os

app = Flask(__name__)

# SECRET KEY
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super_secret_key')

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INIT
CORS(app)
db = SQLAlchemy(app)


# USER MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


# CREATE DATABASE
with app.app_context():
    db.create_all()


# HOME
@app.route('/')
def home():
    return redirect(url_for('login'))


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return 'User already exists'

        # HASH PASSWORD
        hashed_password = generate_password_hash(password)

        # CREATE USER
        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # CHECK HASHED PASSWORD
        if user and check_password_hash(user.password, password):
            session['user'] = username
            return redirect(url_for('page1'))

        return 'Invalid username or password'

    return render_template('login.html')


# PRIVATE PAGE
@app.route('/page1')
def page1():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template(
        'page1.html',
        username=session['user']
    )


# ADMIN PANEL
@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)


# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# RENDER / GUNICORN SUPPORT
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
