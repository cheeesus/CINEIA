# FlaskAPI\app\routes\users.py
from flask import Blueprint, g, jsonify, request
from app.utils.helpers import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_details(user_id): 
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
        user_details = {
            "user_id": result[0][0],
            "email": result[0][1],
            "age": result[0][2],
            "genres": [{"genre_id": row[3], "genre_name": row[4]} for row in result if row[3]],
            "checked_movies": [
                {"movie_id": row[5], "title": row[6], "date": row[7]} 
                for row in result if row[5]
            ]
        }
        print(user_details)
        return jsonify(user_details), 200
    else:
        return jsonify({'error': 'User not found'}), 404


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
