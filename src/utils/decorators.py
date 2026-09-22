from functools import wraps

import jwt
from flask import jsonify, request

from src.config import Config
from src.models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return (
                jsonify(
                    {"error": "Token de autorización requerido en el header"}
                ),
                401,
            )

        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"],
            )

            current_user = User.query.get(payload["user_id"])

            if not current_user:
                return (
                    jsonify(
                        {"error": "El usuario asociado al token no existe"}
                    ),
                    401,
                )

        except jwt.ExpiredSignatureError:
            return (
                jsonify(
                    {
                        "error": (
                            "El token ha expirado. "
                            "Por favor, inicia sesión nuevamente"
                        )
                    }
                ),
                401,
            )

        except jwt.InvalidTokenError:
            return (
                jsonify({"error": "Token de autenticación inválido"}),
                401,
            )

        return f(current_user, *args, **kwargs)

    return decorated