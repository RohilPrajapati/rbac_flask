from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth import validate_registration, validate_login
from app.models import register_user, get_user_with_email
from app.utils.exceptions import ValidationError
from werkzeug.security import check_password_hash


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        next_endpoint = request.form.get("next")
        print(f"next_endpoint: {next_endpoint}")
        try:
            validate_registration(request.form)
            register_user(request.form)

            if next_endpoint:
                try:
                    flash("User added successfully", "success")
                    return redirect(next_endpoint)
                except Exception as e:
                    print(f"error: {e}")
            flash("Sign up completed", "success")
            return redirect(url_for("auth.login"))

        except ValidationError as e:
            message = "Fail to create user" if next_endpoint else "Failed to sign up"
            flash(message, "error")

            return render_template(
                "auth/register.j2",
                next=next_endpoint,
                errors=e.errors,
                form=request.form,
            )
    next_url = request.args.get("next", "")
    return render_template("auth/register.j2", next=next_url)


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        try:
            validate_login(request.form)
            user = get_user_with_email(request.form["email"])
            if not user or not check_password_hash(
                user["password"], request.form["password"]
            ):
                flash("Username or Password is incorrect", "error")
                return render_template("auth/login.j2", form=request.form)

            session["user_id"] = user["id"]
            session["full_name"] = f"{user['first_name']} {user['last_name']}"
            session["role"] = user["role"]

            flash(f"Welcome, {user['first_name']}!", "success")

            next_endpoint = request.args.get("next")
            if next_endpoint:
                try:
                    return redirect(url_for(next_endpoint))
                except:
                    return redirect(url_for("dashboard"))

            return redirect(url_for("dashboard"))

        except ValidationError as e:
            flash("Failed to login up", "error")
            return render_template("auth/login.j2", errors=e.errors, form=request.form)
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("auth/login.j2")


@bp.route("/logout", methods=("GET", "POST"))
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))
