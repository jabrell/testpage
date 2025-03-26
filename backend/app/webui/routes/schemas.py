from typing import Any

import requests
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from ..settings import admin_required, get_fastapi_url

schema_bp = Blueprint("schemas", __name__)


@schema_bp.route("/schemas", methods=["GET", "POST"])
@admin_required
def schemas(header: dict[str, Any]):
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(url_for("schemas"))
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "schema-error")
            return redirect(url_for("schemas"))
        if file:
            # Send the file to the FastAPI endpoint
            response = requests.post(
                f"{get_fastapi_url()}schema",
                files={"file": (file.filename, file.stream, file.mimetype)},
                headers=header,
            )
            if response.status_code == 201:
                flash("Schema created successfully", "schema-success")
                return redirect(url_for("schemas.schemas"))
            else:
                # Display the error message from the FastAPI response
                try:
                    error_message = response.json().get("detail", "An error occurred")
                    flash(error_message, "schema-error")
                    return redirect(url_for("schemas.schemas"))
                except Exception:
                    flash("An error ocurred", "schema-error")
                    return redirect(url_for("home"))

    # Fetch the list of schemas from FastAPI
    response = requests.get(f"{get_fastapi_url()}schema", headers=header)
    if response.status_code == 200:
        schemas = response.json()
        return render_template("schema.html", schemas=schemas)
    return "Failed to fetch schemas", 500


@schema_bp.route("/schema/<int:schema_id>")
@admin_required
def view_schema(schema_id, header: dict[str, Any] | None = None):
    # Fetch the schema details from FastAPI
    fastapi_url = get_fastapi_url()
    response = requests.get(f"{fastapi_url}schema/{schema_id}", headers=header)
    if response.status_code == 200:
        schema = response.json()
        return jsonify(schema["jsonschema"])
    flash("Schema not found", "error")
    return redirect(url_for("schemas"))
