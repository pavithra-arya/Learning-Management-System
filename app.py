from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os

app = Flask(__name__)
# Secure secret key - should be an env variable in production
app.config['SECRET_KEY'] = 'dev_secret_key_12345'
# Using MySQL for development
# Make sure to update 'root' and 'password' if your MySQL credentials are different!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:PSaqvl%4023@localhost/lms_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
from models import db, User
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
from auth import auth as auth_blueprint
from routes.teacher import teacher as teacher_blueprint
from routes.student import student as student_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(teacher_blueprint)
app.register_blueprint(student_blueprint)


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
