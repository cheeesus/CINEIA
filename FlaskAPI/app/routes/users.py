# FlaskAPI\app\routes\users.py
from flask import Blueprint, g, jsonify, request
from app.utils.helpers import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_details(user_id):
    try:
        with g.db.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.id AS user_id,
                    u.email AS user_email,
                    u.age AS user_age,
                    g.id AS genre_id,
                    g.name AS genre_name,
                    vh.movie_id AS viewed_movie_id,
                    m.title AS viewed_movie_title,
                    vh.view_date AS view_date
                FROM
                    users u
                LEFT JOIN
                    user_preferences up ON u.id = up.user_id
                LEFT JOIN
                    genres g ON up.genre_id = g.id
                LEFT JOIN
                    view_history vh ON u.id = vh.user_id
                LEFT JOIN
                    movies m ON vh.movie_id = m.id
                WHERE
                    u.id = %s;
            """, (user_id,))
            result = cursor.fetchall()

        if result:
            # Initialize sets to store unique genres and viewed movies
            # Sets are used for efficient uniqueness checking
            unique_genres = set()
            unique_checked_movies = set()

            user_details = {
                "user_id": result[0][0],
                "email": result[0][1],
                "age": result[0][2],
                "genres": [], # Will be populated with unique genres
                "checked_movies": [] # Will be populated with unique movies
            }

            for row in result:
                # Add unique genres
                genre_id, genre_name = row[3], row[4]
                if genre_id is not None and (genre_id, genre_name) not in unique_genres:
                    user_details["genres"].append({"genre_id": genre_id, "genre_name": genre_name})
                    unique_genres.add((genre_id, genre_name))

                # Add unique checked movies
                movie_id, movie_title, view_date = row[5], row[6], row[7]
                if movie_id is not None and (movie_id, movie_title, view_date) not in unique_checked_movies:
                    # Convert date to string for JSON serialization
                    user_details["checked_movies"].append({
                        "movie_id": movie_id,
                        "title": movie_title,
                        "date": str(view_date) if view_date else None
                    })
                    unique_checked_movies.add((movie_id, movie_title, view_date))

            print(user_details)
            return jsonify(user_details), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500


@users_bp.route('/<int:user_id>/genres', methods=['PUT'])
@token_required
def update_preferred_genres(user_id):

    data = request.get_json()
    preferred_genres = data.get('preferred_genres')

    if not isinstance(preferred_genres, list):
        return jsonify({"error": "preferred_genres must be a list"}), 400

    try:
        with g.db.cursor() as cursor:
        # Fetch genre IDs for the given names
            cursor.execute(
                "SELECT id, name FROM genres WHERE name = ANY(%s)", (preferred_genres,)
            )
            rows = cursor.fetchall()
            # Map genre name -> genre id
            name_to_id = {row[1]: row[0] for row in rows}
            valid_genres = set(name_to_id.keys())
            print(f"Valid genres: {valid_genres}")

            invalid_genres = set(preferred_genres) - valid_genres
            if invalid_genres:
                return jsonify({"error": f"Invalid genre names: {list(invalid_genres)}"}), 400

            # Delete old preferences for this user
            cursor.execute(
                "DELETE FROM user_preferences WHERE user_id = %s", (user_id,)
            )

            # Insert new preferences using the genre IDs
            for genre_name in preferred_genres:
                genre_id = name_to_id[genre_name]
                cursor.execute(
                    "INSERT INTO user_preferences (user_id, genre_id) VALUES (%s, %s)",
                    (user_id, genre_id)
                )

        g.db.commit()


        return jsonify({"message": "Preferred genres updated successfully"}), 200

    except Exception as e:
        g.db.rollback()
        print(f"Error updating genres: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@users_bp.route('/<int:user_id>/lists', methods=['GET'])
@token_required
def get_user_lists(user_id : int):
    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                l.id AS list_id,
                l.name AS list_name
            FROM 
                lists l
            WHERE 
                l.user_id = %s;
        """, (user_id,))
        result = cursor.fetchall()
    
    if result:
        lists = lists = [
            {"list_id": row[0], "list_name": row[1]} for row in result
        ]
        return jsonify(lists), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@users_bp.route('/<int:user_id>/<int:list_id>/add', methods=['POST'])
@token_required
def add_to_existing_list(user_id: int, list_id: int):
    try:
        data = request.get_json()
        movie_id = data.get('movieId')

        if not movie_id:
            return jsonify({"error": "movieId is required"}), 400

        with g.db.cursor() as cursor:
            # Check if the movie exists in the movies table
            cursor.execute("SELECT id FROM movies WHERE id = %s", (movie_id,))
            if cursor.fetchone() is None:
                return jsonify({"error": f"Movie with ID {movie_id} does not exist"}), 404

            # Check if the list exists for the user
            cursor.execute("SELECT id FROM lists WHERE id = %s AND user_id = %s", (list_id, user_id))
            if cursor.fetchone() is None:
                return jsonify({"error": f"List with ID {list_id} does not exist for user {user_id}"}), 404

            # Check if the movie is already in the list
            cursor.execute(
                "SELECT 1 FROM list_movies WHERE list_id = %s AND movie_id = %s",
                (list_id, movie_id)
            )
            if cursor.fetchone():
                return jsonify({"error": "Movie already exists in the list"}), 409

            # Add the movie to the list
            cursor.execute("INSERT INTO list_movies (list_id, movie_id) VALUES (%s, %s)", (list_id, movie_id))
            g.db.commit()

        return jsonify({"message": "Movie added to the list successfully"}), 200

    except Exception as e:
        g.db.rollback()  # Rollback in case of any error
        return jsonify({"error": f"Failed to add movie to list: {str(e)}"}), 500

@users_bp.route('/<int:user_id>/popular-by-preference', methods=['GET'])
@token_required
def get_popular_movies_by_user_preferences(user_id: int):
    try:
        with g.db.cursor() as cursor:
            # 1. Fetch user's preferred genre IDs and names
            # Join user_preferences with the genres table to get the genre name
            cursor.execute("""
                SELECT up.genre_id, g.name AS genre_name
                FROM user_preferences up
                JOIN genres g ON up.genre_id = g.id
                WHERE up.user_id = %s
            """, (user_id,))
            preferred_genres = cursor.fetchall()

            if not preferred_genres:
                return jsonify({"message": "No preferred genres found for this user."}), 404

            # 2. Fetch most popular movies for each preferred genre
            genre_movie_map = {}
            for genre_id, genre_name in preferred_genres:
                # Assuming 'popularity' column exists in the 'movies' table
                # If not, use m.release_date DESC or another metric
                cursor.execute("""
                    SELECT m.id, m.title, m.poster_path, m.release_date, m.popularity
                    FROM movies m
                    JOIN movie_genre mg ON m.id = mg.movie_id
                    WHERE mg.genre_id = %s
                    ORDER BY m.popularity DESC
                    LIMIT 10
                """, (genre_id,))
                movies = cursor.fetchall()

                # Convert tuple results to dictionaries for better readability in JSON
                genre_movie_map[genre_name] = [
                    {
                        "movie_id": movie[0],
                        "title": movie[1],
                        "poster_url": "https://image.tmdb.org/t/p/w500" + movie[2] if movie[2] else None,
                        "release_date": str(movie[3]), 
                        "popularity": movie[4]
                    }
                    for movie in movies
                ]

        return jsonify({"popular_movies": genre_movie_map}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        # Log the error for debugging
        return jsonify({"message": "An internal server error occurred."}), 500