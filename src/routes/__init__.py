from flask import Flask

from src.routes.health import health_bp
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.matchmaking import matchmaking_bp
from src.routes.leaderboard import leaderboard_bp

def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(user_bp, url_prefix="/api/v1/user")
    app.register_blueprint(matchmaking_bp, url_prefix="/api/v1/matchmaking")
    app.register_blueprint(leaderboard_bp, url_prefix="/api/v1/leaderboard")
