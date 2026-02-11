from flask import Blueprint, render_template, request

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        return "Form submitted ! process is will implemented soon"
    return render_template("auth/register.j2")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        return "Form submitted ! process is will implemented soon"
    return render_template("auth/login.j2")
