import psycopg2
from flask import g, current_app

def db_connect(app):
    @app.before_request
    def connect_db():
        if 'db' not in g:
            try:
                g.db = psycopg2.connect(
                    host=app.config['DB_HOST'],
                    database=app.config['DB_NAME'],
                    user=app.config['DB_USER'],
                    password=app.config['DB_PASSWORD']
                )
                current_app.logger.info("Database connection successful.")
            except psycopg2.OperationalError as e:
                current_app.logger.error(f"Database connection failed: {e}")
                raise

    @app.teardown_request
    def close_db(exception):
        db = g.pop('db', None)
        if db:
            db.close()