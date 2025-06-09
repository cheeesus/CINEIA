# FlaskAPI\app\routes\movies.py
from flask import Blueprint, g, jsonify, request
from functools import wraps
from app.utils.helpers import token_required

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/recent', methods=['GET'])
def get_movies_recent():
    page = int(request.args.get('page', 1))  # Get the page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # Get the limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, vote_average, release_date, poster_path, 
                   vote_count, budget, popularity, runtime, director 
            FROM movies 
            ORDER BY release_date DESC LIMIT %s OFFSET %s
        """, (limit, offset))
        movies = cursor.fetchall()
        movies_list = [
        {
            'id': movie[0],
            'title': movie[1],
            'vote_average': movie[2],
            'release_date': movie[3],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie[4]}" if movie[4] else None,
            'vote_count': movie[5],
            'budget': movie[6],
            'popularity': movie[7],
            'runtime': movie[8],
            'director': movie[9]
        }
        for movie in movies
    ]
    return jsonify(movies_list), 200

@movies_bp.route('/top', methods=['GET'])
def get_movies_top():
    page = int(request.args.get('page', 1))  # page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, vote_average, release_date, poster_path,
                   vote_count, budget, popularity, runtime, director 
            FROM movies
            ORDER BY vote_average DESC LIMIT %s OFFSET %s
        """, (limit, offset))
        movies = cursor.fetchall()
        movies_list = [
        {
            'id': movie[0],
            'title': movie[1],
            'vote_average': movie[2],
            'release_date': movie[3],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie[4]}" if movie[4] else None,
            'vote_count': movie[5],
            'budget': movie[6],
            'popularity': movie[7],
            'runtime': movie[8],
            'director': movie[9]
        }
        for movie in movies
    ]
    return jsonify(movies_list), 200

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, overview, poster_path, release_date, director, 
                   is_adult, budget, original_language, popularity, revenue, 
                   runtime, vote_average, vote_count
            FROM movies 
            WHERE id = %s
        """, (movie_id,))
        movie = cursor.fetchone()
    if movie:
        movie_details = {
            'id': movie[0],
            'title': movie[1],
            'overview': movie[2],
            'poster_url': "https://image.tmdb.org/t/p/w500" + movie[3] if movie[3] else None,
            'release_date': movie[4],
            'director': movie[5],
            'is_adult': movie[6],
            'budget': movie[7],
            'original_language': movie[8],
            'popularity': movie[9],
            'revenue': movie[10],
            'runtime': movie[11],
            'vote_average': movie[12],
            'vote_count': movie[13]
        }
        return jsonify(movie_details), 200
    else:
        return jsonify({'error': 'Movie not found'}), 404

@movies_bp.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', "").strip()  # Get the search query from parameters
    page = int(request.args.get('page', 1))  # Default page is 1
    limit = int(request.args.get('limit', 24))  # Default limit is 24 movies per request

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    offset = (page - 1) * limit  # Calculate offset for pagination
    query_terms = query.split()
    like_patterns = [f"%{term}%" for term in query_terms]

    # Dynamically create the SQL placeholders
    title_conditions = " OR ".join(["m.title ILIKE %s"] * len(query_terms))
    keyword_conditions = " OR ".join(["k.name = %s"] * len(query_terms))

    query_values = like_patterns + query_terms + [limit, offset]
    with g.db.cursor() as cursor:
        cursor.execute(f"""
            SELECT m.id, m.title, m.vote_average, m.release_date, m.poster_path
            FROM movies m
            LEFT JOIN movie_keyword mk ON m.id = mk.movie_id
            LEFT JOIN keywords k ON mk.keyword_id = k.id
            WHERE ({title_conditions})
            OR ({keyword_conditions})
            GROUP BY m.id
            ORDER BY m.release_date DESC
            LIMIT %s OFFSET %s;
            """, query_values)

        movies = cursor.fetchall()
        movies_list = [
            {
                'id': movie[0],
                'title': movie[1],
                'vote_average': movie[2],
                'release_date': movie[3],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie[4]}" if movie[4] else None
            }
            for movie in movies
        ]

    return jsonify({"movies": movies_list}), 200

@movies_bp.route('/<int:movie_id>/add-to-list', methods=['POST'])
@token_required
def add_movie_to_list():
    movie_id = request.view_args['movie_id']  # Extract movie_id from the route
    user_id = g.user_id  # Use user_id from the token

    data = request.get_json()
    list_name = data.get('list_name')

    if not list_name:
        return jsonify({'error': 'List name is required'}), 400

    with g.db.cursor() as cursor:
        # Check if the list exists or create a new one
        cursor.execute("""
            INSERT INTO lists (user_id, name)
            VALUES (%s, %s)
            ON CONFLICT (user_id, name) DO NOTHING
            RETURNING id
        """, (user_id, list_name))
        list_id_row = cursor.fetchone()

        if not list_id_row:
            cursor.execute("""
                SELECT id FROM lists WHERE user_id = %s AND name = %s
            """, (user_id, list_name))
            list_id_row = cursor.fetchone()

        list_id = list_id_row[0]

        # Add the movie to the list
        cursor.execute("""
            INSERT INTO list_movies (list_id, movie_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (list_id, movie_id))
        g.db.commit()

    return jsonify({'message': f'Movie added to list "{list_name}" successfully'}), 200

@movies_bp.route('/<int:movie_id>/rate', methods=['POST'])
@token_required
def rate_movie():
    movie_id = request.view_args['movie_id']  # Extract movie_id from the route
    user_id = g.user_id  # Use user_id from the token

    data = request.get_json()
    rating = data.get('rating')

    if not (0 <= rating <= 10):
        return jsonify({'error': 'Rating must be between 0 and 10'}), 400

    with g.db.cursor() as cursor:
        # Insert or update the rating for the movie by the user
        cursor.execute("""
            INSERT INTO ratings (user_id, movie_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, movie_id)
            DO UPDATE SET rating = EXCLUDED.rating
        """, (user_id, movie_id, rating))
        g.db.commit()

    return jsonify({'message': 'Movie rated successfully'}), 200

@movies_bp.route('/<int:movie_id>/favorite', methods=['POST'], endpoint="add_favorite")
@token_required
def add_movie_to_favorites():
    movie_id = request.view_args['movie_id']  # Extract movie_id from the route
    user_id = g.user_id  # Use user_id from the token

    with g.db.cursor() as cursor:
        # Ensure the "favorites" list exists for the user
        cursor.execute("""
            INSERT INTO lists (user_id, name)
            VALUES (%s, 'favorites')
            ON CONFLICT (user_id, name) DO NOTHING
            RETURNING id
        """, (user_id,))
        favorites_list_id = cursor.fetchone()[0]

        # Add the movie to the "favorites" list
        cursor.execute("""
            INSERT INTO list_movies (list_id, movie_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (favorites_list_id, movie_id))
        g.db.commit()

    return jsonify({"message": "Movie added to favorites successfully"}), 200

@movies_bp.route('/<int:movie_id>/favorite', methods=['DELETE'], endpoint="remove_favorite")
@token_required
def remove_movie_from_favorites():
    movie_id = request.view_args['movie_id']  # Extract movie_id from the route
    user_id = g.user_id  # Use user_id from the token

    with g.db.cursor() as cursor:
        # Remove the movie from the "favorites" list
        cursor.execute("""
            DELETE FROM list_movies
            WHERE movie_id = %s AND list_id = (
                SELECT id FROM lists WHERE user_id = %s AND name = 'favorites'
            )
        """, (movie_id, user_id))
        g.db.commit()

    return jsonify({"message": "Movie removed from favorites successfully"}), 200
