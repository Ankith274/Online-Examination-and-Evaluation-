import os
import json
from datetime import datetime
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_sys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@app.template_filter('fromjson')
def fromjson_filter(value):
    return json.loads(value)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
from auth.routes import auth_bp
from admin.routes import admin_bp
from faculty.routes import faculty_bp
from student.routes import student_bp
from exam.routes import exam_bp
from evaluation.routes import evaluation_bp
from ml.routes import ml_bp

# Set bcrypt instance for auth blueprint so it doesn't need to create a new one, or we just let it use its own uninitialized instance for hashing checking (wait, check_password_hash works statically, but flask-bcrypt Bcrypt() without app needs to be passed app or we used it correctly).
# Actually, it's cleaner to just register blueprints here.
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(student_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(evaluation_bp)
app.register_blueprint(ml_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'Teacher':
            return redirect(url_for('faculty.teacher_dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student.student_dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(role='Admin').first():
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password=hashed_password, role='Admin', is_approved=True)
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin / admin123")
    app.run(debug=True, port=5000)
