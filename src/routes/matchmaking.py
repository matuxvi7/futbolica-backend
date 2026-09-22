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
    """
    Sumarse a la cola de emparejamiento 1v1
    ---
    tags:
    - Matchmaking

    parameters: [{name: Authorization, in: header, type: string, required: true, description: "Token JWT en formato: Bearer <TOKEN>"}]

    responses: {200: {description: Entró en la cola o encontró partida de inmediato, schema: {type: object, properties: {status: {type: string, example: matched}, match_id: {type: string, example: match_07f24103}, message: {type: string, example: "Buscando rival..."}, players: {type: array, items: {type: object, properties: {user_id: {type: string, example: "07f24103-975b-4bf7-9276-899dc2aa0073"}, username: {type: string, example: jugador1}, elo: {type: integer, example: 1200}}}}}}}, 400: {description: Ya se encuentra en la cola de búsqueda, schema: {type: object, properties: {message: {type: string, example: "Ya estás en la cola de búsqueda."}}}}, 401: {description: Token ausente o inválido, schema: {type: object, properties: {error: {type: string, example: "Token ausente o inválido"}}}}}
    """
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
    """
    Cancelar busqueda y salir de la cola de emparejamiento
    ---
    tags:
    - Matchmaking
    
    parameters: [{name: Authorization, in: header, type: string, required: true, description: "Token JWT en formato: Bearer <TOKEN>"}]

    responses: {200: {description: Removido con éxito de la cola de búsqueda, schema: {type: object, properties: {message: {type: string, example: "Has salido de la cola de búsqueda."}}}}, 400: {description: El usuario no estaba en la cola, schema: {type: object, properties: {message: {type: string, example: "No estabas en la cola."}}}}, 401: {description: Token ausente o inválido, schema: {type: object, properties: {error: {type: string, example: "Token ausente o inválido"}}}}}
    """
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
    """
    Consultar estado de la busqueda o partida encontrada
    ---
    tags: 
    - Matchmaking

    parameters: [{name: Authorization, in: header, type: string, required: true, description: "Token JWT en formato: Bearer <TOKEN>"}]

    responses: {200: {description: Estado actual de la búsqueda (queued/idle) o datos de la partida encontrada (matched), schema: {type: object, properties: {status: {type: string, example: queued}, in_queue: {type: boolean, example: true}, match_id: {type: string, example: match_07f24103}, players: {type: array, items: {type: object, properties: {user_id: {type: string, example: "07f24103-975b-4bf7-9276-899dc2aa0073"}, username: {type: string, example: jugador1}, elo: {type: integer, example: 1200}}}}}}}, 401: {description: Token ausente o inválido, schema: {type: object, properties: {error: {type: string, example: "Token ausente o inválido"}}}}}
    """
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