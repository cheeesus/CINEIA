from app.routes.auth import auth_bp
from app.routes.movies import movies_bp



def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(movies_bp, url_prefix='/movies')
    