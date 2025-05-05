import psycopg2
from flask import g

def db_connect(app):
    @app.before_request
    def connect_db():
        if 'db' not in g:
            g.db = psycopg2.connect(
                host=app.config['DB_HOST'],
                database=app.config['DB_NAME'],
                user=app.config['DB_USER'],
                password=app.config['DB_PASSWORD']
            )
    
    @app.teardown_request
    def close_db(exception):
        db = g.pop('db', None)
        if db:
            db.close()
