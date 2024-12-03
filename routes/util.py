import hashlib
from functools import wraps
from flask import session, jsonify

# ChatGPT lol
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if 'username' or 'email' is in the session
        if "username" not in session or "email" not in session:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    return wrapper
