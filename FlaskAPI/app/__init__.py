# FlaskAPI\app\__init__.py
import os
from flask import Flask
from flask_cors import CORS
from app.connectDB import db_connect
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    
    # Enable CORS for all routes
    # CORS(app, supports_credentials=True)
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    # init db connection
    db_connect(app)

    # register blueprints
    register_routes(app)


    return app


