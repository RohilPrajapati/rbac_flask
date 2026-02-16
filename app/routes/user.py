from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import fetch_list_users, delete_user, get_user_by_id, update_user
from app.utils.decorators import role_required
from app.services.auth import validate_user_update
from app.utils.exceptions import ValidationError


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("", methods=("GET",))
@role_required("super_admin")
def list_user_view():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    show_form = request.args.get("create", "").lower() == "true"

    data = fetch_list_users(page, page_size)
    return render_template(
        "user/user_list.j2",
        template_name="user/user_list.j2",
        show_form=show_form,
        **data,
    )


@bp.route("/<int:user_id>", methods=("GET",))
@role_required("super_admin")
def detail_user_view(user_id: int):
    user = get_user_by_id(user_id)
    if user:
        return render_template("user/detail_user.j2", user_id=user["id"], user=user)
    return render_template("404.j2")


@bp.route("/<int:user_id>/update", methods=("GET", "POST"))
@role_required("super_admin")
def update_user_view(user_id):
    user = get_user_by_id(user_id)
    if request.method == "POST":
        print()
        try:
            validate_user_update(request.form)
            update_user(request.form)

            flash("User updated successfully", "success")
            return redirect(url_for("user.list_user_view"))
        except ValidationError as e:
            print(f"validation error {e.errors}")
            flash("Fail to update user", "error")

            return render_template(
                "user/update_user.j2",
                errors=e.errors,
                user_id=user["id"],
                form=request.form,
            )

    return render_template("user/update_user.j2", user_id=user["id"], form=user)


@bp.route("/<int:user_id>/delete", methods=("POST",))
@role_required("super_admin")
def delete_user_view(user_id):
    if request.method == "POST":
        try:
            delete_user(user_id)
            flash("User deleted successfully", "success")
        except ValueError as e:
            flash(str(e), "error")

    return redirect(url_for("user.list_user_view"))
