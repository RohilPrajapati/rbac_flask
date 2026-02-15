from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.decorators import role_required
from app.models import (
    fetch_list_artist,
    create_artist,
    get_artist_by_id,
    update_artist,
    delete_artist,
    fetch_list_music,
)
from app.services.artist import validate_artist
from app.utils.exceptions import ValidationError

bp = Blueprint("artist", __name__, url_prefix="/artist")


@bp.route("", methods=("GET",))
@role_required("super_admin", "artist_manager")
def list_artist_view():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)

    data = fetch_list_artist(page, page_size)
    print(data)
    return render_template(
        "artist/list_artist.j2",
        template_name="artist/list_artist.j2",
        **data,
    )


@bp.route("/create", methods=("GET", "POST"))
@role_required("super_admin", "artist_manager")
def create_artist_view():
    if request.method == "POST":
        try:
            validate_artist(request.form)
            create_artist(request.form)

            flash("Artist created successfully", "success")
            return redirect(url_for("artist.list_artist_view"))
        except ValidationError as e:
            print(f"validation error {e.errors}")
            flash("Fail to update artist", "error")

            return render_template(
                "artist/form_artist.j2",
                errors=e.errors,
                form=request.form,
            )
    return render_template("artist/form_artist.j2")


@bp.route("/<int:artist_id>", methods=("GET",))
@role_required("super_admin", "artist_manager")
def detail_artist_view(artist_id: int):
    artist = get_artist_by_id(artist_id)
    music = fetch_list_music(artist_id)
    if artist:
        return render_template(
            "artist/detail_artist.j2",
            artist_id=artist["id"],
            artist=artist,
            music=music,
        )
    return render_template("404.j2")


@bp.route("/<int:artist_id>/update", methods=("GET", "POST"))
@role_required("super_admin", "artist_manager")
def update_artist_view(artist_id):
    artist = get_artist_by_id(artist_id)
    if request.method == "POST":
        print()
        try:
            validate_artist(request.form)
            update_artist(request.form)

            flash("Artist updated successfully", "success")
            return redirect(url_for("artist.list_artist_view"))
        except ValidationError as e:
            print(f"validation error {e.errors}")
            flash("Fail to update artist", "error")

            return render_template(
                "artist/form_artist.j2",
                errors=e.errors,
                artist_id=artist["id"],
                form=request.form,
            )

    return render_template("artist/form_artist.j2", artist_id=artist["id"], form=artist)


@bp.route("/<int:artist_id>/delete", methods=("POST",))
@role_required("super_admin", "artist_manager")
def delete_artist_view(artist_id):
    if request.method == "POST":
        try:
            delete_artist(artist_id)
            flash("Artist deleted successfully", "success")
        except ValueError as e:
            flash(str(e), "error")

    return redirect(url_for("user.list_artist_view"))
