from flask import Flask, jsonify
import psycopg2

# Informations de connexion à PostgreSQL
HOST = "postgresql-yannr.alwaysdata.net"
DATABASE = "yannr_00"       
USER = "yannr_01"       
PASSWORD = "Projet1234" 

# Initialiser Flask
app = Flask(__name__)

# Variable globale pour stocker les données des films (mise en cache)
movies_cache = {}

# Fonction de connexion à la base de données
def get_db_connection():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )

# Fonction pour récupérer les films **une seule fois**
def fetch_movies_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer tous les films
        all_movies_query = "SELECT id, is_adult, title, popularity, release_date, runtime, vote_average, vote_count, director FROM movies;"
        cursor.execute(all_movies_query)
        movies_data = cursor.fetchall()

        movies_dict = {
            row[0]: {
                "is_adult": row[1],
                "title": row[2],
                "popularity": row[3],
                "release_date": row[4],
                "runtime": row[5],
                "vote_average": row[6],
                "vote_count": row[7],
                "director": row[8],
                "genres": [],
                "keywords": []
            }
            for row in movies_data
        }

        # Récupérer les genres
        genres_query = """
        SELECT mg.movie_id, g.name
        FROM movie_genre mg
        JOIN genres g ON mg.genre_id = g.id;
        """
        cursor.execute(genres_query)
        genres_data = cursor.fetchall()

        for movie_id, genre in genres_data:
            if movie_id in movies_dict:
                movies_dict[movie_id]["genres"].append(genre)

        # Récupérer les keywords
        keywords_query  = """
        SELECT mk.movie_id, k.name
        FROM movie_keyword mk
        JOIN keywords k ON mk.keyword_id = k.id;
        """
        cursor.execute(keywords_query)
        keywords_data = cursor.fetchall()

        for movie_id, keyword in keywords_data:
            if movie_id in movies_dict:
                movies_dict[movie_id]["keywords"].append(keyword)

        # Fermer la connexion
        cursor.close()
        conn.close()

        return movies_dict
    except Exception as e:
        print(f"Erreur de récupération des données : {e}")
        return {}

# Charger les films **au démarrage** (mise en cache)
movies_cache = fetch_movies_data()




# Route API qui retourne les films **sans refaire la requête SQL**
@app.route("/movies/429", methods=["GET"])
def get_movie_429():
    return jsonify(movies_cache.get(429, {"error": "Film non trouvé"}))

if __name__ == "__main__":
    app.run(debug=True)