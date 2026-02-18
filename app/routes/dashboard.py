from app.utils.decorators import login_required
from flask import render_template, session
from app.models import dashboard_data


def register_dashboard_routes(app):

    @app.route("/dashboard")
    @login_required
    def dashboard():
        data = {}
        if session.get("role") in ["super_admin", "artist_manager"]:
            data = dashboard_data()
        return render_template("dashboard.j2", data=data)
