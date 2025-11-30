from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import Config
from datetime import timedelta, datetime, date

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Make datetime utilities available in Jinja2 templates
    app.jinja_env.globals.update(
        timedelta=timedelta,
        datetime=datetime,
        date=date
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Create database and default admin
    with app.app_context():
        db.create_all()
        create_default_admin()
        create_default_departments()

    return app

def create_default_admin():
    """Create default admin user if not exists"""
    admin = User.query.filter_by(role='admin', username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created - Username: admin, Password: admin123")

def create_default_departments():
    """Create default departments if not exists"""
    from app.models import Department
    
    departments = [
        {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
        {'name': 'Neurology', 'description': 'Brain and nervous system'},
        {'name': 'Orthopedics', 'description': 'Bones and muscles'},
        {'name': 'Pediatrics', 'description': 'Children healthcare'},
        {'name': 'Dermatology', 'description': 'Skin conditions'},
        {'name': 'General Medicine', 'description': 'General health issues'},
    ]
    
    for dept_data in departments:
        dept = Department.query.filter_by(name=dept_data['name']).first()
        if not dept:
            dept = Department(**dept_data)
            db.session.add(dept)
    
    db.session.commit()
