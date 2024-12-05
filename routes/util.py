from functools import wraps
from flask import session, jsonify

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if 'USER_ID' is in the session
        user_id = session.get("USER_ID")
        if not user_id:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        # Pass user_id to the wrapped function
        return func(user_id=user_id, *args, **kwargs)
    return wrapper
