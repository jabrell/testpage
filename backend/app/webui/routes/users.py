from typing import Any

import requests
from fastapi import status
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..settings import admin_required, get_fastapi_url

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["GET", "POST"])
@admin_required
def users(header: dict[str, Any]):
    if request.method == "POST":
        user = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "is_superuser": True if request.form.get("is_superuser") else False,
            "is_active": True if request.form.get("is_active") else False,
            "usergroup_name": request.form.get("usergroup_name"),
        }
        response = requests.post(
            f"{get_fastapi_url()}user/create",
            json=user,
            headers=header,
        )
        if response.status_code == status.HTTP_201_CREATED:
            flash("User created successfully", "user-success")
            return redirect(url_for("users.users"))
        else:
            try:
                error_message = response.json().get("detail", "An error occurred")
                flash(error_message, "user-error")
            except Exception:
                flash("An error occurred", "user-error")

    # get request
    response = requests.get(f"{get_fastapi_url()}user", headers=header)
    if response.status_code == status.HTTP_200_OK:
        users = response.json()
        return render_template("user.html", users=users)
    return "Failed to fetch users", 500
