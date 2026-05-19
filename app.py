import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.config import config
from backend.database.db import init_db
from backend.routes.chat import chat_bp
from backend.routes.booking import booking_bp
from backend.routes.auth import auth_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
    app.config.from_object(config)

    CORS(app, resources={r"/api/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "OPTIONS"],
    }})

    app.register_blueprint(chat_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def static_proxy(path: str):
        return send_from_directory(app.static_folder, path)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
