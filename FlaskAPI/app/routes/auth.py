# API/app/routes/auth.py
import base64
import binascii
from flask import Blueprint, request, jsonify, g, make_response
from app.utils.helpers import hash_password, verify_password, generate_token
from app.connectDB import db_connect

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    selected_genres = data.get('selectedGenres')  

    # Hash password for security
    hashed_password = hash_password(password)

    # Simple validation
    if not email or not password or not age:
        return jsonify({"error": "All fields are required"}), 400

    try:
        cursor = g.db.cursor()

        # Insert user into the `users` table and get user_id
        cursor.execute(
            "INSERT INTO users (email, password_hash, age) VALUES (%s, %s, %s) RETURNING id",
            (email, hashed_password, age)
        )
        user_id = cursor.fetchone()[0]  # Fetch the generated user_id

        # Map genre names to their IDs
        if selected_genres and isinstance(selected_genres, list):
            # Query to get genre IDs for the given genre names
            format_strings = ','.join(['%s'] * len(selected_genres))
            cursor.execute(
                f"SELECT id FROM genres WHERE name IN ({format_strings})",
                tuple(selected_genres)
            )
            genre_ids = [row[0] for row in cursor.fetchall()]

            # Insert user preferences
            preferences = [(user_id, genre_id) for genre_id in genre_ids]
            cursor.executemany(
                "INSERT INTO user_preferences (user_id, genre_id) VALUES (%s, %s)",
                preferences
            )

        g.db.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        g.db.rollback()  # Rollback in case of any error
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    # Get JSON data from the request body
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Basic validation: Ensure email and password are provided
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Query for the user with the given email
        with g.db.cursor() as cursor:
            cursor.execute("SELECT id, email, encode(password_hash, 'escape') as password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if user :
            print(f"Stored Hash: {user[2]}") 
            print(f"Entered Password: {password}")
            if verify_password(password, user[2]) :
                token = generate_token({"user_id": user[0], "email": user[1]})
                response = make_response(jsonify({"user_id": user[0], "email": user[1], "token": token}))
                response.set_cookie("token", token, httponly=True, secure=True)
                return response, 200  
        # If authentication fails
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500