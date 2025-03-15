# load_data.py
import pandas as pd
from sqlalchemy import create_engine
import psycopg2


def get_db_engine():
    """Établit et retourne un engine SQLAlchemy pour la connexion à la base de données."""
    HOST = "postgresql-rospars.alwaysdata.net"
    USER = "rospars_01"
    PASSWORD = "Projet1234"
    DATABASE = "rospars_yann"
    PORT = 5432  # Port par défaut de PostgreSQL

    try:
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        return engine
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

engine = get_db_engine()

if engine:
    # Récupérer les films
    query = "SELECT id, title, overview, popularity, vote_average FROM movies;"
    movies_df = pd.read_sql(query, engine)

    # Charger les genres
    query_genres = "SELECT id, name FROM genres;"
    genres_df = pd.read_sql(query_genres, engine)

    # Charger les mots-clés
    query_keywords = "SELECT id, name FROM keywords;"
    keywords_df = pd.read_sql(query_keywords, engine)

    # Charger la table movies_genre
    query_movies_genre = "SELECT movie_id, genre_id FROM movie_genre;"
    movies_genre_df = pd.read_sql(query_movies_genre, engine)

    # Charger la table movies_keyword
    query_movies_keyword = "SELECT movie_id, keyword_id FROM movie_keyword;"
    movies_keyword_df = pd.read_sql(query_movies_keyword, engine)

    engine.dispose()  # Fermer la connexion