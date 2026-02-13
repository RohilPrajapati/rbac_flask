from flask import Flask, redirect, url_for
from app.config import SECRET_KEY


def create_app():
    app = Flask(__name__)

    app.secret_key = SECRET_KEY

    @app.route("/hello-world")
    def hello():
        return "Hello, World !"

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    from app.routes import auth
    from app.routes.dashboard import register_dashboard_routes

    register_dashboard_routes(app)

    app.register_blueprint(auth.bp)

    return app
