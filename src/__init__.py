from flask import Flask

from src.config import Config
from src.extensions import db, migrate, sock
import src.models


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    sock.init_app(app)

    from src.routes import register_routes
    from src.routes.realtime import register_realtime_routes

    register_routes(app)
    register_realtime_routes(sock)

    @app.cli.command("seed")
    def seed_command():
        from src.seeds import seed_db
        seed_db()

    return app