from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    from app.routes import auth_bp, professor_bp, student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(student_bp)

    return app