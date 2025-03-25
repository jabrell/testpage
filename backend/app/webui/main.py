import requests
from fastapi import status
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.core.config import settings

app = Flask(__name__)
app.secret_key = "supersecretkey"
FASTAPI_URL = "http://127.0.0.1:8000/api/v1/"  # Update with your FastAPI URL


def get_fastapi_url():
    return FASTAPI_URL


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # TODO how to handle that the first superuser is not in the database but any
    # admin user is?
    if not username == settings.FIRST_SUPERUSER:
        return "Login failed", 401
    response = requests.post(
        f"{get_fastapi_url()}login/access_token",
        data={"username": username, "password": password},
    )
    if response.status_code == 200:
        session["token"] = response.json()["access_token"]
        return redirect(url_for("schemas"))
    return redirect(url_for("home"))


@app.route("/schemas", methods=["GET", "POST"])
def schemas():
    a_token = session.get("token")
    header = {"Authorization": f"Bearer {a_token}"}
    # TODO test if the token is valid
    if not a_token:
        return redirect(url_for("home"))
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(url_for("schemas"))
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(url_for("schemas"))
        if file:
            # Send the file to the FastAPI endpoint
            response = requests.post(
                f"{get_fastapi_url()}schema",
                files={"file": (file.filename, file.stream, file.mimetype)},
                headers=header,
            )
            if response.status_code == 201:
                flash("Schema created successfully", "success")
                return redirect(url_for("schemas"))
            if response.status_code == status.HTTP_403_FORBIDDEN:
                flash("Forbidden", "error")
                return redirect(url_for("home"))
            else:
                # TODO better handling of expired token error
                # Display the error message from the FastAPI response
                try:
                    error_message = response.json().get("detail", "An error occurred")
                    flash(error_message, "error")
                    return redirect(url_for("schemas"))
                except Exception:
                    return redirect(url_for("home"))

    # Fetch the list of schemas from FastAPI
    response = requests.get(f"{get_fastapi_url()}schema")
    if response.status_code == 200:
        schemas = response.json()
        return render_template("schema.html", schemas=schemas)
    return "Failed to fetch schemas", 500


@app.route("/schema/<int:schema_id>")
def view_schema(schema_id):
    # Fetch the schema details from FastAPI
    fastapi_url = get_fastapi_url()
    response = requests.get(f"{fastapi_url}schema/{schema_id}")
    if response.status_code == 200:
        schema = response.json()
        return jsonify(schema["jsonschema"])
    flash("Schema not found", "error")
    return redirect(url_for("schemas"))
