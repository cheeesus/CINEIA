from flask import Blueprint, g, jsonify, request

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    page = int(request.args.get('page', 1))  # Get the page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # Get the limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("SELECT id, title, poster_path FROM movies LIMIT %s OFFSET %s", (limit, offset))
        movies = cursor.fetchall()
        movies_list = [
        {
            'id': movie[0],
            'title': movie[1],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie[2]}" if movie[2] else None
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
