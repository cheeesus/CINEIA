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
        # Query for the user with the given email
        with g.db.cursor() as cursor:
            cursor.execute("SELECT id, email, encode(password_hash, 'escape') as password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if user :
            print(f"Stored Hash: {user[2]}") 
            print(f"Entered Password: {password}")
            if verify_password(password, user[2]) :
                token = generate_token({"user_id": user[0], "email": user[1]})
                response = make_response(jsonify({"email": user[1], "token": token}))
                response.set_cookie("token", token, httponly=True, secure=True)
                return response, 200  
        
        # If authentication fails
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500