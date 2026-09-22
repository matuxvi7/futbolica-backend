from flask import Flask

from src.routes.health import health_bp
from src.routes.auth import auth_bp
from src.routes.user import user_bp

def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(user_bp, url_prefix="/api/v1/user")