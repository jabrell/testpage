import requests
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .routes import schema_bp, user_bp
from .settings import get_fastapi_url

app = Flask(__name__)

app.register_blueprint(schema_bp)
app.register_blueprint(user_bp)
# TODO move this to settings
app.secret_key = "supersecretkey"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    response = requests.post(
        f"{get_fastapi_url()}login/access_token",
        data={"username": username, "password": password},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        response = requests.get(
            f"{get_fastapi_url()}user/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        if not response.status_code == 200:
            return "Login failed", 401
        user = response.json()
        if not response.json()["is_superuser"]:
            return "Login failed", 401
        session["token"] = token
        session["user"] = user
        session["is_admin"] = user["is_superuser"]
        session["auth_header"] = {"Authorization": f"Bearer {token}"}
        return redirect(url_for("schemas.schemas"))
    return redirect(url_for("home"))
