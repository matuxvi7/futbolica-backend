import jwt
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room

from src.config import Config
from src.extensions import db
from src.models import User


socketio = SocketIO(cors_allowed_origins="*")


# Diccionario para mapear socket_id -> user_data
CONNECTED_USERS = {}


@socketio.on("connect")
def handle_connect(auth):
    """Maneja la conexión WebSocket con autenticación JWT vía handshake."""
    token = None

    if auth and isinstance(auth, dict):
        token = auth.get("token")

    if not token:
        # Intentar extraer desde query params ?token=xxx
        token = request.args.get("token")

    if not token:
        # Rechazar conexión sin token
        return False

    try:
        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"],
        )

        user_id = payload["user_id"]
        user = User.query.get(user_id)

        if not user:
            return False

        CONNECTED_USERS[request.sid] = {
            "user_id": str(user.id),
            "username": user.username,
            "room": None,
        }

        emit(
            "authenticated",
            {
                "status": "connected",
                "user_id": str(user.id),
                "username": user.username,
            },
        )

        print(
            f"🔌 WebSocket conectado: {user.username} "
            f"(sid: {request.sid})"
        )

    except Exception as e:
        print(f"❌ Error de autenticación en WS: {e}")
        return False


@socketio.on("disconnect")
def handle_disconnect():
    """Maneja la desconexión del cliente WebSocket."""
    user_info = CONNECTED_USERS.pop(request.sid, None)

    if user_info:
        print(
            f"🔌 WebSocket desconectado: "
            f"{user_info['username']}"
        )


@socketio.on("join_match_room")
def handle_join_match_room(data):
    """Une al jugador a la sala privada de la partida."""
    match_id = data.get("match_id")
    user_info = CONNECTED_USERS.get(request.sid)

    if match_id and user_info:
        join_room(match_id)
        user_info["room"] = match_id

        emit(
            "player_joined_room",
            {
                "message": (
                    f"{user_info['username']} "
                    f"se unió a la sala {match_id}"
                ),
                "username": user_info["username"],
            },
            to=match_id,
        )