from flask import Blueprint, jsonify, request

from src.services.auth import authenticate_user, register_user


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth",
)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
    - Autenticación

    parameters: [{in: body, name: body, required: true, schema: {type: object, required: [username, email, password], properties: {username: {type: string, example: jugador1}, email: {type: string, example: "jugador1@example.com"}, password: {type: string, example: "Password123!"}}}}]

    responses: {201: {description: Usuario registrado con éxito, schema: {type: object, properties: {message: {type: string, example: "Usuario registrado con éxito"}, user: {type: object, properties: {id: {type: string, example: "9b720883-d3ef-4a6f-baa8-275cacceda6e"}, username: {type: string, example: jugador3}, email: {type: string, example: "jugador1@example.com"}, elo_rating: {type: integer, example: 1200}, created_at: {type: string, example: "2026-09-22T19:43:26.478539+00:00"}, stats: {type: object, properties: {wins: {type: integer, example: 0}, losses: {type: integer, example: 0}, matches_played: {type: integer, example: 0}}}}}}}}, 400: {description: Datos faltantes o usuario/email ya existente, schema: {type: object, properties: {error: {type: string, example: "Faltan campos obligatorios (username, email, password)"}}}}}
    """
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
    """
    Iniciar sesión y obtener token JWT
    ---
    tags:
    - Autenticación

    parameters: [{in: body, name: body, required: true, schema: {type: object, required: [username, password], properties: {username: {type: string, example: jugador1}, password: {type: string, example: "Password123!"}}}}]

    responses: {200: {description: Autenticación exitosa con token JWT, schema: {type: object, properties: {message: {type: string, example: "Autenticación exitosa"}, token: {type: string, example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}, user: {type: object, properties: {id: {type: string, example: "9b720883-d3ef-4a6f-baa8-275cacceda6e"}, username: {type: string, example: jugador3}, email: {type: string, example: "jugador1@example.com"}, elo_rating: {type: integer, example: 1200}, created_at: {type: string, example: "2026-09-22T19:43:26.478539+00:00"}, stats: {type: object, properties: {wins: {type: integer, example: 0}, losses: {type: integer, example: 0}, matches_played: {type: integer, example: 0}}}}}}}}, 400: {description: Faltan campos requeridos, schema: {type: object, properties: {error: {type: string, example: "Se requiere usuario/email y contraseña"}}}}, 401: {description: Credenciales inválidas, schema: {type: object, properties: {error: {type: string, example: "Credenciales inválidas"}}}}}
    """
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