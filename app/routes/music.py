from flask import render_template, request, flash, redirect, url_for, Blueprint
from app.utils.decorators import role_required
from app.utils.exceptions import ValidationError
from app.models import create_music, delete_music, get_music_by_id, update_music
from app.services.music import validate_music
from app.utils.urls import is_safe_url

bp = Blueprint("music", __name__, url_prefix="/music")


@bp.route("/artist/<int:artist_id>/create", methods=("GET", "POST"))
@role_required("super_admin", "artist_manager", "artist")
def create_music_for_artist_view(artist_id):
    if request.method == "POST":
        try:
            validate_music(request.form)
            create_music(request.form)
            flash("Music created successfully", "success")
            next_endpoint = request.form.get("next")
            if next_endpoint and is_safe_url(next_endpoint):
                try:
                    return redirect(next_endpoint)
                except Exception as e:
                    print(f"error: {e}")
            return redirect(url_for("artist.detail_artist_view", artist_id=artist_id))
        except ValidationError as e:
            flash("Fail to update artist", "error")

            return render_template(
                "music/form_music_with_artist_id.j2",
                next=next_endpoint,
                errors=e.errors,
                form=request.form,
            )
    next_endpoint = request.args.get("next")
    return render_template(
        "music/form_music_with_artist_id.j2", artist_id=artist_id, next=next_endpoint
    )


@bp.route("/<int:music_id>/update", methods=("GET", "POST"))
@role_required("super_admin", "artist_manager", "artist")
def update_music_view(music_id):
    music = get_music_by_id(music_id)
    if request.method == "POST":
        try:
            validate_music(request.form)
            update_music(request.form)

            next_endpoint = request.form.get("next")
            if next_endpoint and is_safe_url(next_endpoint):
                try:
                    return redirect(next_endpoint)
                except Exception as e:
                    print(f"error: {e}")
            flash("Music updated successfully", "success")
            return redirect(
                url_for("artist.detail_artist_view", artist_id=music["artist_id"])
            )
        except ValidationError as e:
            flash("Fail to update music", "error")

            return render_template(
                "music/form_music_with_artist_id.j2",
                errors=e.errors,
                music_id=music["id"],
                form=request.form,
            )
    next_endpoint = request.args.get("next")
    return render_template(
        "music/form_music_with_artist_id.j2",
        music_id=music_id,
        artist_id=music["artist_id"],
        form=music,
        next=next_endpoint,
    )


@bp.route("/<int:music_id>/delete", methods=("POST",))
@role_required("super_admin", "artist_manager", "artist")
def delete_music_view(music_id):
    if request.method == "POST":
        music = get_music_by_id(music_id)
        try:
            delete_music(music_id)
            flash("Artist deleted successfully", "success")
        except ValueError as e:
            flash(str(e), "error")
    next = request.args.get("next")
    if next and is_safe_url(next):
        return redirect(next)
    return redirect(url_for("artist.detail_artist_view", artist_id=music["artist_id"]))
