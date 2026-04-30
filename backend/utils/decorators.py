from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*rol_idler):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol_id not in rol_idler:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
