from flask import Blueprint, jsonify, request

from src.services.auth import authenticate_user, register_user


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth",
)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return (
            jsonify(
                {
                    "error": (
                        "Faltan campos obligatorios "
                        "(username, email, password)"
                    )
                }
            ),
            400,
        )

    result = register_user(
        username,
        email,
        password,
    )

    if not result["success"]:
        return jsonify({"error": result["error"]}), 400

    return (
        jsonify(
            {
                "message": "Usuario registrado con éxito",
                "user": result["user"],
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    username_or_email = data.get("username") or data.get("email")
    password = data.get("password")

    if not username_or_email or not password:
        return (
            jsonify(
                {
                    "error": (
                        "Se requiere usuario/email "
                        "y contraseña"
                    )
                }
            ),
            400,
        )

    result = authenticate_user(
        username_or_email,
        password,
    )

    if not result["success"]:
        return jsonify({"error": result["error"]}), 401

    return (
        jsonify(
            {
                "message": "Autenticación exitosa",
                "token": result["token"],
                "user": result["user"],
            }
        ),
        200,
    )