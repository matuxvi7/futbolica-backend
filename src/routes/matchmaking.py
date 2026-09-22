from flask import Blueprint, jsonify

from src.models import User
from src.services.matchmaking import matchmaking_service
from src.utils.decorators import token_required


matchmaking_bp = Blueprint(
    "matchmaking",
    __name__,
    url_prefix="/api/v1/matchmaking",
)


@matchmaking_bp.route("/join", methods=["POST"])
@token_required
def join_queue(current_user: User):
    """Suma al usuario autenticado a la cola de emparejamiento."""
    added = matchmaking_service.add_player(
        user_id=str(current_user.id),
        username=current_user.username,
        elo=current_user.elo_rating,
    )

    if not added:
        return jsonify({"message": "Ya estás en la cola de búsqueda."}), 400

    # Intentar emparejar de inmediato
    match = matchmaking_service.find_match(str(current_user.id))

    if match:
        p1, p2, match_id = match

        return (
            jsonify(
                {
                    "status": "matched",
                    "match_id": match_id,
                    "players": [p1, p2],
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "status": "queued",
                "message": "Buscando rival...",
            }
        ),
        200,
    )


@matchmaking_bp.route("/leave", methods=["POST"])
@token_required
def leave_queue(current_user: User):
    """Cancela la búsqueda y saca al usuario de la cola."""
    removed = matchmaking_service.remove_player(str(current_user.id))

    if removed:
        return (
            jsonify({"message": "Has salido de la cola de búsqueda."}),
            200,
        )

    return jsonify({"message": "No estabas en la cola."}), 400


@matchmaking_bp.route("/status", methods=["GET"])
@token_required
def check_status(current_user: User):
    """Consulta si se encontró partida o sigue en búsqueda."""
    user_id = str(current_user.id)

    match = matchmaking_service.find_match(user_id)

    if match:
        p1, p2, match_id = match

        return (
            jsonify(
                {
                    "status": "matched",
                    "match_id": match_id,
                    "players": [p1, p2],
                }
            ),
            200,
        )

    in_queue = user_id in matchmaking_service.queue

    return (
        jsonify(
            {
                "status": "queued" if in_queue else "idle",
                "in_queue": in_queue,
            }
        ),
        200,
    )