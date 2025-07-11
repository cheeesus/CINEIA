# FlaskAPI\app\routes\movies.py
from app.utils.helpers import token_required
from flask import Blueprint, g, jsonify, request

import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))


from DNN_TorchFM_TTower.service.recommender import recommend_movies_for_user
from DNN_TorchFM_TTower.models.db import get_movie_titles

movies_bp = Blueprint('movies', __name__)

@movies_bp.get("/<int:user_id>/recommend")
def recommend(user_id: int):
    top = int(request.args.get("top", 10))

    # Step 1: Get recommended movie IDs and scores
    mids, scores, strategy = recommend_movies_for_user(user_id, n_final=top)
    mids_py = [int(x) for x in mids]

    # Step 2: Query database for additional movie details
    with g.db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, release_date, poster_path, vote_average
            FROM movies 
            WHERE id = ANY(%s) AND vote_average > 0
            """, 
            (mids_py,)
        )
        movie_details = {row[0]: {"title": row[1], "release_date": row[2], "poster_url": f"https://image.tmdb.org/t/p/w500{row[3]}" if row[3] else None, 'rating': row[4]} 
                         for row in cursor.fetchall()}
    # Step 3: Build response with details
    return jsonify({
        "user_id": user_id,
        "strategy": strategy,  # cold | warm+rank
        "items": [
            {
                "rank": i + 1,
                "id": mid,
                "title": movie_details.get(mid, {}).get("title", "Unknown"),
                "release_date": movie_details.get(mid, {}).get("release_date"),
                "poster_url": movie_details.get(mid, {}).get("poster_url"),
                "rating": movie_details.get(mid, {}).get("rating"),
                "score": float(scores[i]) if scores[i] is not None else None
            }
            for i, mid in enumerate(mids_py)
        ]
    })

@movies_bp.route('/recent', methods=['GET'])
def get_movies_recent():
    page = int(request.args.get('page', 1))  # Get the page number from query parameter (default is 1)
    limit = int(request.args.get('limit', 24))  # Get the limit (number of movies per page)
    
    offset = (page - 1) * limit  # Calculate the offset for SQL query

    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, release_date, poster_path, vote_average
            FROM movies 
            WHERE vote_average > 0
            ORDER BY release_date DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        movies = cursor.fetchall()
        movies_list = [
        {
            'id': movie[0],
            'title': movie[1],
            'release_date': movie[2],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie[3]}" if movie[3] else None,
            'rating': movie[4]
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
            SELECT id, title, release_date, poster_path, vote_average
            FROM movies
            WHERE vote_average > 0
            ORDER BY vote_average DESC LIMIT %s OFFSET %s
        """, (limit, offset))
        movies = cursor.fetchall()
        movies_list = [
        {
            'id': movie[0],
            'title': movie[1],
            'release_date': movie[2],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie[3]}" if movie[3] else None,
            'rating': movie[4]
        }
        for movie in movies
    ]
    return jsonify(movies_list), 200

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id: int):
    with g.db.cursor() as cursor:
        # Récupérer les informations du film
        cursor.execute("""
            SELECT id, title, overview, poster_path, release_date, director, 
                   is_adult, budget, original_language, popularity, revenue, 
                   runtime, vote_average, vote_count, backdrop_path
            FROM movies 
            WHERE id = %s
        """, (movie_id,))
        movie = cursor.fetchone()
        
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        
        cursor.execute("""
            SELECT g.name 
            FROM movie_genre mg
            JOIN genres g ON mg.genre_id = g.id
            WHERE mg.movie_id = %s
        """, (movie_id,))
        genres = cursor.fetchall()
        
        # Récupérer les acteurs du film avec leurs rôles et URL de profil
        cursor.execute("""
            SELECT a.id, a.actor_name, a.profile_path, c.movie_character
            FROM actors a
            JOIN casting c ON a.id = c.actor_id
            WHERE c.movie_id = %s
        """, (movie_id,))
        actors = cursor.fetchall()

        
        
    # Formater les informations du film
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
        'vote_count': movie[13],
        'backdrop_url': "https://image.tmdb.org/t/p/w500" + movie[14] if movie[14] else None,
        'genres': [genre[0] for genre in genres],
        'actors': []
    }
    
    # Ajouter les informations des acteurs
    for actor in actors:
        movie_details['actors'].append({
            'actor_id': actor[0],
            'actor_name': actor[1],
            'profile_url': "https://image.tmdb.org/t/p/w500" + actor[2] if actor[2] else None,
            'character': actor[3]
        })
    
    return jsonify(movie_details), 200




# add movie to view history
@movies_bp.route('/<int:user_id>/history', methods=['POST'])
@token_required
def add_to_view_history(user_id : int):
    data = request.json
    movie_id = data.get('movie_id')

    if not movie_id:
        return jsonify({"error": "Movie ID is required"}), 400

    with g.db.cursor() as cursor:
        # Check if the movie already exists in the history
        cursor.execute("""
            SELECT COUNT(*) FROM view_history
            WHERE user_id = %s AND movie_id = %s
        """, (user_id, movie_id))
        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute("""
                INSERT INTO view_history (user_id, movie_id, view_date)
                VALUES (%s, %s, NOW())
            """, (user_id, movie_id))
            g.db.commit()

    return jsonify({"message": "Movie added to view history"}), 201

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
            SELECT m.id, m.title, m.release_date, m.poster_path, m.vote_average
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
                'release_date': movie[2],
                'poster_url': "https://image.tmdb.org/t/p/w500" + movie[3] if movie[3] else None,
                'rating': movie[4]
            }
            for movie in movies
        ]

    return jsonify({"movies": movies_list}), 200


@movies_bp.route('/<int:movie_id>/add-to-list', methods=['POST'])
@token_required
def add_movie_to_list(movie_id : int):
    user_id = g.user['user_id']  # Use user_id from the token

    data = request.get_json()
    list_name = data.get('list_name')
    print(f"list to add to: {list_name}")

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
def rate_movie(movie_id : int):
    user_id = g.user['user_id']  # Use user_id from the token

    data = request.get_json()
    rating = data.get('rating') 

    if not (0 <= rating <= 10):
        return jsonify({'error': 'Rating must be between 0 and 10'}), 400

    with g.db.cursor() as cursor:
        # Insert or update the rating for the movie by the user
        cursor.execute("""
            INSERT INTO users_ratings (user_id, movie_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, movie_id)
            DO UPDATE SET rating = EXCLUDED.rating
        """, (user_id, movie_id, rating))
        g.db.commit()

    return jsonify({'message': 'Movie rated successfully'}), 200

@movies_bp.route('/<int:movie_id>/rating', methods=['GET'])
@token_required
def get_user_rating(movie_id):
    user_id = g.user['user_id']  
    with g.db.cursor() as cursor :
        cursor.execute(""" 
            SELECT rating, user_id, movie_id 
            FROM users_ratings 
            WHERE user_id = %s AND movie_id = %s
        """,(user_id, movie_id,))

        rating = cursor.fetchone()

    if not rating:
        return jsonify({"user_rating": None}), 200

    return jsonify({"user_rating": rating[0], "user_id": rating[1], "movie_id": rating[2]}), 200

@movies_bp.route('/<int:movie_id>/favorite', methods=['POST'], endpoint="add_favorite")
@token_required
def add_movie_to_favorites(movie_id: int):
    user_id = g.user['user_id']  # Use user_id from the token

    with g.db.cursor() as cursor:
        # Try inserting the favorites list, or do nothing if it exists
        cursor.execute("""
            INSERT INTO lists (user_id, name)
            VALUES (%s, 'favorites')
            ON CONFLICT (user_id, name) DO NOTHING
            RETURNING id
        """, (user_id,))
        result = cursor.fetchone()

        if result is None:
            # favorites list already exists, fetch its id
            cursor.execute("""
                SELECT id FROM lists WHERE user_id = %s AND name = 'favorites'
            """, (user_id,))
            result = cursor.fetchone()
        
        favorites_list_id = result[0]

        # Add the movie to the favorites list
        cursor.execute("""
            INSERT INTO list_movies (list_id, movie_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (favorites_list_id, movie_id))
        g.db.commit()

    return jsonify({"message": "Movie added to favorites successfully"}), 200


@movies_bp.route('/<int:movie_id>/favorite', methods=['DELETE'], endpoint="remove_favorite")
@token_required
def remove_movie_from_favorites(movie_id : int):
    user_id = g.user['user_id']  # Use user_id from the token

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

@movies_bp.route('/<int:list_id>/movies', methods=['GET'])
@token_required
def get_all_movies_in_list(list_id: int):
    with g.db.cursor() as cursor : 
        cursor.execute("""
            SELECT movie_id FROM list_movies WHERE list_id = %s 
        """, (list_id,))
        movies = cursor.fetchall()
        movie_ids = [movie[0] for movie in movies]

        return jsonify({"movie_ids": movie_ids})
    
@movies_bp.route('/<int:list_id>', methods=['DELETE'])
@token_required
def delete_list(list_id: int):
    with g.db.cursor() as cursor:
        # Delete the list's movies
        cursor.execute("DELETE FROM list_movies WHERE list_id = %s", (list_id,))
        # Delete the list itself
        cursor.execute("DELETE FROM lists WHERE id = %s", (list_id,))
        g.db.commit()
        return jsonify({"message": "List deleted successfully"}), 200

@movies_bp.route('/<int:list_id>/movies/<int:movie_id>', methods=['DELETE'])
@token_required
def delete_movie_from_list(list_id: int, movie_id: int):
    with g.db.cursor() as cursor:
        # Vérifier si le film appartient à la liste
        cursor.execute("""
            SELECT * FROM list_movies WHERE list_id = %s AND movie_id = %s
        """, (list_id, movie_id))
        movie_entry = cursor.fetchone()
        if not movie_entry:
            return jsonify({"message": "Movie not found in the specified list"}), 404
        # Supprimer le film de la liste
        cursor.execute("""
            DELETE FROM list_movies WHERE list_id = %s AND movie_id = %s
        """, (list_id, movie_id))
        g.db.commit()
        return jsonify({"message": "Movie deleted successfully from the list"}), 200
    


@movies_bp.route('/<int:movie_id>/comments', methods=['GET'])
def get_comments(movie_id: int):
    with g.db.cursor() as cursor:
        # Fetch email directly from the database
        cursor.execute("""
            SELECT 
                ur.movie_id, 
                ur.user_id, 
                ur.rate_date, 
                ur.comment, 
                u.email, 
                u.age
            FROM 
                users_ratings ur
            JOIN 
                users u
            ON 
                ur.user_id = u.id
            WHERE 
                ur.movie_id = %s AND ur.comment IS NOT NULL
        """, (movie_id,))
        comments = cursor.fetchall()

    if not comments:
        return jsonify({"message": "No comments found for this movie."}), 404

    # Process the data to derive usernames in Python
    processed_comments = []
    for comment in comments:
        print(comment)  # For debugging
        username = comment[4].split('@')[0]  # Derive username from email
        processed_comments.append({
            "movie_id": comment[0],
            "user_id": comment[1],
            "comment": comment[3],
            "rating": None,  # Assuming 'rating' is missing in your query
            "created_at": comment[2],
            "username": username,
            "age": comment[5]
        })

    return jsonify(processed_comments), 200


@movies_bp.route('/<int:movie_id>/comments', methods=['POST'])
@token_required
def add_comment(movie_id: int):
    user_id = g.user['user_id']
    data = request.get_json()
    username = data.get("username")
    
    # Validate input
    if not data or not data.get("comment"):
        return jsonify({"error": "Comment is required"}), 400

    with g.db.cursor() as cursor:
        # Check if the user has already rated the movie
        cursor.execute("""
            SELECT rating FROM users_ratings 
            WHERE user_id = %s AND movie_id = %s
        """, (user_id, movie_id))
        existing_rating = cursor.fetchone()

        if not existing_rating:
            return jsonify({"error": "You need to rate the movie before commenting"}), 400

        # Update the comment for the existing rating
        cursor.execute("""
            UPDATE users_ratings
            SET comment = %s, rate_date = NOW()
            WHERE user_id = %s AND movie_id = %s
            RETURNING movie_id, user_id, comment, rating, rate_date
        """, (data["comment"], user_id, movie_id))
        updated_comment = cursor.fetchone()
    g.db.commit()
    return jsonify({
        "movie_id": updated_comment[0],
        "user_id": updated_comment[1],
        "username": username,
        "comment": updated_comment[2],
        "rating": updated_comment[3],
        "updated_at": updated_comment[4]
    }), 200


# PUT: Update a comment
# @movies_bp.route('/<int:movie_id>/comments/<int:comment_id>', methods=['PUT'])
# @token_required
# def update_comment(movie_id: int, comment_id: int):
#     user_id = g.user['user_id']
#     data = request.get_json()

#     if not data or not data.get("content") or not data.get("rating"):
#         return jsonify({"error": "Updated content and rating are required"}), 400

#     with g.db.cursor() as cursor:
#         # Verify that the comment exists and belongs to the current user
#         cursor.execute("""
#             SELECT id FROM comments WHERE id = %s AND movie_id = %s AND user_id = %s
#         """, (comment_id, movie_id, user_id))
#         comment = cursor.fetchone()

#         if not comment:
#             return jsonify({"error": "Comment not found or unauthorized"}), 404

#         # Update the comment
#         cursor.execute("""
#             UPDATE comments
#             SET content = %s, rating = %s, updated_at = NOW()
#             WHERE id = %s
#             RETURNING id, movie_id, user_id, username, content, rating, created_at, updated_at
#         """, (data["content"], data["rating"], comment_id))
#         updated_comment = cursor.fetchone()

#     return jsonify({
#         "id": updated_comment.id,
#         "movie_id": updated_comment.movie_id,
#         "user_id": updated_comment.user_id,
#         "username": updated_comment.username,
#         "content": updated_comment.content,
#         "rating": updated_comment.rating,
#         "created_at": updated_comment.created_at,
#         "updated_at": updated_comment.updated_at
#     }), 200

# # DELETE: Remove a comment
# @movies_bp.route('/<int:movie_id>/comments/<int:comment_id>', methods=['DELETE'])
# @token_required
# def delete_comment(movie_id: int, comment_id: int):
#     user_id = g.user['user_id']

#     with g.db.cursor() as cursor:
#         # Verify that the comment exists and belongs to the current user
#         cursor.execute("""
#             SELECT id FROM comments WHERE id = %s AND movie_id = %s AND user_id = %s
#         """, (comment_id, movie_id, user_id))
#         comment = cursor.fetchone()

#         if not comment:
#             return jsonify({"error": "Comment not found or unauthorized"}), 404

#         # Delete the comment
#         cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))

#     return jsonify({"message": "Comment deleted successfully"}), 200