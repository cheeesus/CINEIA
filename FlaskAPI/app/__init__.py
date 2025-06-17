# FlaskAPI\app\__init__.py
import os
from flask import Flask
from flask_cors import CORS
from app.connectDB import db_connect
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    
    # Enable CORS for specific origins
    CORS(app, resources={r"/api/*": {"origins": ["http://45.149.207.13:3100"]}}, supports_credentials=True)

    # Initialize other components
    db_connect(app)
    register_routes(app)

    return app