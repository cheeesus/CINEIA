import bcrypt
from functools import wraps
import jwt
import hashlib
from flask import request, jsonify, current_app, g

def hash_password(password):
   return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(payload):
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token and verify logic
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token missing"}), 403
        try:
            user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user_id = user["user_id"]  # Set `g.user_id` globally
        except Exception as e:
            return jsonify({"error": "Token invalid or expired"}), 403
        return f(*args, **kwargs)
    return decorated_function
