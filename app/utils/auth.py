from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask import jsonify, current_app

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get('role') != role:
                    return jsonify({"error": "Access denied"}), 403
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 401
        return decorator
    return wrapper

def get_current_user():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        from app.models.user import User
        return User.query.get(user_id)
    except Exception:
        return None