from flask import Flask, jsonify
from app.db import get_connection


def create_app():
    app = Flask(__name__)

    @app.route("/hello-world")
    def hello():
        return "Hello, World !"

    return app
