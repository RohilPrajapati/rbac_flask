from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "error")
            return redirect(url_for("auth.login", next=request.endpoint))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    """
    Example:
    @role_required("super_admin")
    @role_required("artist", "artist_manager")
    """

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):

            if "user_id" not in session:
                flash("Please login first.", "error")
                return redirect(url_for("auth.login", next=request.endpoint))

            user_role = session.get("role")

            if user_role not in roles:
                flash("You are not authorized to access this page.", "error")
                return redirect(url_for("dashboard"))

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
