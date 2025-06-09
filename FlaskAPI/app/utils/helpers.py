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
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            token = token.split("Bearer ")[1]  # Extract token part
            user_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user = user_data  # Attach user info to Flask's `g` object
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 403

        return f(*args, **kwargs)
    return decorated_function

