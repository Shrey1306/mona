"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

from .routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../../../templates")
    CORS(app)
    register_routes(app)
    return app

