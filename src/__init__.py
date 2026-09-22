from flask import Flask

from src.config import Config
from src.extensions import db, migrate, sock, swagger
from src.cli import register_cli_commands
from src.events import socketio

import src.models


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)

    app.config["SWAGGER"] = {
        "title": "Futbolica API",
        "uiversion": 3,
    }

    db.init_app(app)
    migrate.init_app(app, db)
    sock.init_app(app)
    socketio.init_app(app)
    swagger.init_app(app)

    from src.routes import register_routes
    from src.routes.realtime import register_realtime_routes

    register_routes(app)
    register_realtime_routes(sock)

    register_cli_commands(app)

    return app