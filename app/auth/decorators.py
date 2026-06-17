from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def roles_required(*role_names: str):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role_name not in role_names:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
