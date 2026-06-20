from flask import Flask

from .config import Config
from .routes import main_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    return app
