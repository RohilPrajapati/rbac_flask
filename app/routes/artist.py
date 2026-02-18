from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)
from app.utils.decorators import role_required
from app.models import (
    fetch_list_artist,
    create_artist,
    create_artists_bulk,
    get_artist_by_id,
    update_artist,
    delete_artist,
    fetch_list_music,
    get_all_artists,
    get_artist_by_user_id,
)
from app.services.artist import validate_artist
from app.utils.exceptions import ValidationError
import io
import csv

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


@bp.route("/file/create", methods=["POST"])
@role_required("super_admin", "artist_manager")
def create_artist_from_file():
    REQUIRED_COLUMNS = {
        "name",
        "dob",
        "gender",
        "address",
        "first_release_year",
        "no_of_albums",
    }
    file = request.files.get("file")
    if not file:
        flash("Please Upload File", "error")
        return redirect(url_for("artist.list_artist_view"))
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        csv_columns = set(csv_reader.fieldnames or [])

        missing_columns = REQUIRED_COLUMNS - csv_columns
        if missing_columns:
            flash(f"Missing columns: {', '.join(missing_columns)}", "error")
            return redirect(url_for("artist.list_artist_view"))

        artists_to_insert = []

        for row in csv_reader:
            if not row.get("name"):
                continue

            artists_to_insert.append(
                {
                    "name": row.get("name"),
                    "dob": row.get("dob"),
                    "gender": row.get("gender"),
                    "address": row.get("address"),
                    "first_release_year": row.get("first_release_year"),
                    "no_of_albums": row.get("no_of_albums"),
                }
            )

        if not artists_to_insert:
            flash("No valid records found.", "error")
            return redirect(url_for("artist.list_artist_view"))

        create_artists_bulk(artists_to_insert)

        flash(f"{len(artists_to_insert)} artists created successfully!", "success")
        return redirect(url_for("artist.list_artist_view"))

    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("artist.list_artist_view"))


@bp.route("/file/export", methods=["GET"])
@role_required("super_admin", "artist_manager")
def export_artist_to_file():
    try:
        artists = get_all_artists()

        output = io.StringIO()
        writer = csv.writer(output)

        # No ID column
        writer.writerow(
            [
                "name",
                "dob",
                "gender",
                "address",
                "first_release_year",
                "no_of_albums",
            ]
        )

        for artist in artists:
            writer.writerow(
                [
                    artist["name"],
                    artist["dob"],
                    artist["gender"],
                    artist["address"],
                    artist["first_release_year"],
                    artist["no_of_albums"],
                ]
            )

        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="artists_export.csv",
        )

    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("artist.list_artist_view"))


@bp.route("/<int:artist_id>", methods=("GET",))
@role_required("super_admin", "artist_manager")
def detail_artist_view(artist_id: int):
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)

    artist = get_artist_by_id(artist_id)
    music = fetch_list_music(artist_id, page, page_size)
    if artist:
        return render_template(
            "artist/detail_artist.j2",
            artist_id=artist["id"],
            artist=artist,
            music=music,
        )
    return render_template("404.j2")


@bp.route("user/<int:user_id>", methods=("GET",))
@role_required("artist")
def get_artist_by_user(user_id: int):
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)

    artist = get_artist_by_user_id(user_id)
    if artist:
        music = fetch_list_music(artist["id"], page, page_size)
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
