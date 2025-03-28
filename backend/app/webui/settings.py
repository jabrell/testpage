from functools import wraps

from flask import redirect, session, url_for

from app.core.config import settings

# FASTAPI_URL = "http://127.0.0.1:8000/api/v1/"  # Update with your FastAPI URL


def get_fastapi_url() -> str:
    return settings.BACKEND_URL_API_V1


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("home"))
        return f(*args, **kwargs, header=session.get("auth_header"))

    return decorated_function
