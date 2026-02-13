from app.utils.decorators import login_required
from flask import render_template


def register_dashboard_routes(app):

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.j2")
