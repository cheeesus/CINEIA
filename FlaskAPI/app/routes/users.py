# FlaskAPI\app\routes\users.py
from flask import Blueprint, g, jsonify, request
from functools import wraps
from app.utils.helpers import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods = ['GET'])
def get_user_details(user_id): 
    with g.db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                u.id AS user_id,
                u.email AS user_email,
                u.age AS user_age,
                g.id AS genre_id,
                g.name AS genre_name
            FROM 
                users u
            LEFT JOIN 
                user_preferences up ON u.id = up.user_id
            LEFT JOIN 
                genres g ON up.genre_id = g.id
            WHERE 
                u.id = %s;
        """, (user_id,))
        result = cursor.fetchall()
    if result:
        user_details = {
            "user_id": result[0][0],
            "email": result[0][1],
            "age": result[0][2],
            "genres": [{"genre_id": row[3], "genre_name": row[4]} for row in result if row[3]]
        }
        print(user_details)
        return jsonify(user_details), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@users_bp.route('/<int:user_id>/genres', methods=['PUT'])

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