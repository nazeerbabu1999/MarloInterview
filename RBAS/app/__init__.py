from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

db = SQLAlchemy()
jwt = JWTManager()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['JWT_SECRET_KEY'] = 'XGCHCckucjvhljf%^%7KCHGTFKyth'
   
    db.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    
    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.data import data_blueprint
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(data_blueprint, url_prefix='/data')

    with app.app_context():
        # Import models to ensure they're known to SQLAlchemy
        from .models import UserPermission
        # Create initial roles
        db.create_all()
        UserPermission.create_initial_roles()

    # Use Flask's before_first_request to start scheduler
    @app.before_request
    def init_scheduler():
        from .utils.scheduler import start_scheduler
        start_scheduler()

    return app