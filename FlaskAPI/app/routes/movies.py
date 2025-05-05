# FlaskAPI\app\routes\movies.py
from flask import Blueprint, g, jsonify, request

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/recent', methods=['GET'])
def get_movies_recent():
    page = int(request.args.get('page', 1))  # Get the page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # Get the limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("SELECT id, title, vote_average, release_date, poster_path FROM movies ORDER BY release_date DESC LIMIT %s OFFSET %s", (limit, offset))
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
    return jsonify(movies_list), 200

@movies_bp.route('/top', methods=['GET'])
def get_movies_top():
    page = int(request.args.get('page', 1))  # Get the page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # Get the limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("SELECT id, title, vote_average, release_date, poster_path FROM movies ORDER BY vote_average DESC LIMIT %s OFFSET %s", (limit, offset))
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

    with g.db.cursor() as cursor:
        # Use ILIKE for case-insensitive search in PostgreSQL (use LIKE for MySQL)
        cursor.execute(
            """
            SELECT id, title, vote_average, release_date, poster_path 
            FROM movies 
            WHERE title ILIKE %s 
            ORDER BY release_date DESC 
            LIMIT %s OFFSET %s
            """, 
            (f"%{query}%", limit, offset)
        )

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
