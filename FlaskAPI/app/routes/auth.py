# API/app/routes/auth.py
from flask import Blueprint, request, jsonify, g
from app.utils.helpers import hash_password, verify_password, generate_token
from app.connectDB import db_connect

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')

    # Hash password for security
    hashed_password = hash_password(password)

    # Simple validation (you can improve this with more checks)
    if not email or not password or not age:
        return jsonify({"error": "All fields are required"}), 400
    
    try:
        # Use the existing database connection from g.db
        cursor = g.db.cursor()
        cursor.execute("INSERT INTO users (email, password_hash, age) VALUES (%s, %s, %s)", (email, hashed_password, age))
        g.db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
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
        # Query the database for the user with the given email
        with g.db.cursor() as cursor:
            cursor.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        # Check if the user exists and the password is correct
        if user and verify_password(password, user[2]):  # Assuming the password hash is in the 3rd column (index 2)
            # Generate a token with user ID
            token = generate_token({"user_id": user[0]})
            return jsonify({"email": user[1], "token": token}), 200
        
        # If authentication fails
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        # Catch any exceptions and print them for debugging
        print(f"Error during login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500