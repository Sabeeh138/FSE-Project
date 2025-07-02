from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hospital.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key')
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app)
    Migrate(app, db)
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth.routes import auth
    from app.main.routes import main
    from app.patients.routes import patients
    from app.doctors.routes import doctors
    from app.nurses.routes import nurses
    from app.receptionists.routes import receptionists
    from app.store.routes import store
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(patients)
    app.register_blueprint(doctors)
    app.register_blueprint(nurses)
    app.register_blueprint(receptionists)
    app.register_blueprint(store)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app