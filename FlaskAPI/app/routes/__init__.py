# FlaskAPI\app\routes\__init__.py
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.movies import movies_bp



def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')