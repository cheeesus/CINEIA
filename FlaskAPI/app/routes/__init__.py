# FlaskAPI\app\routes\__init__.py
from app.routes.auth import auth_bp
from app.routes.movies import movies_bp
from app.routes.recommend import bp as rec_bp  


def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(rec_bp, url_prefix='/api')