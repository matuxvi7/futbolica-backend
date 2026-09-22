import time

from flask import Blueprint, jsonify, request

from src.models import User


leaderboard_bp = Blueprint(
    "leaderboard",
    __name__,
    url_prefix="/api/v1/leaderboard",
)


# Cache simple en memoria con totales de paginación
LEADERBOARD_CACHE = {
    "data": None,
    "total_users": 0,
    "total_pages": 0,
    "expires_at": 0,
}

CACHE_TTL_SECONDS = 60


@leaderboard_bp.route("", methods=["GET"])
def get_leaderboard():
    """
    Obtener Tabla de Clasificación Global (Leaderboard)
    ---
    tags:
    - Leaderboard

    parameters: [{name: page, in: query, type: integer, required: false, default: 1}, {name: limit, in: query, type: integer, required: false, default: 50}]

    responses: {200: {description: Lista de jugadores ordenada por Elo Rating, schema: {type: object, properties: {source: {type: string, example: cache}, page: {type: integer, example: 1}, limit: {type: integer, example: 50}, total_pages: {type: integer, example: 1}, total_users: {type: integer, example: 4}, leaderboard: {type: array, items: {type: object, properties: {id: {type: string, example: "67889e95-c22a-4782-80e1-d364fc138e4d"}, rank: {type: integer, example: 1}, username: {type: string, example: tester_conector}, elo_rating: {type: integer, example: 1216}, stats: {type: object, properties: {wins: {type: integer, example: 1}, losses: {type: integer, example: 0}, matches_played: {type: integer, example: 1}, win_rate_percentage: {type: number, example: 100.0}}}}}}}}}}
    """


    now = time.time()

    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 50, type=int), 100)

    # Si la consulta es la página 1 por defecto y la cache está vigente,
    # responder desde memoria con la estructura completa.
    if (
        page == 1
        and LEADERBOARD_CACHE["data"]
        and now < LEADERBOARD_CACHE["expires_at"]
    ):
        return (
            jsonify(
                {
                    "source": "cache",
                    "page": 1,
                    "limit": limit,
                    "total_users": LEADERBOARD_CACHE["total_users"],
                    "total_pages": LEADERBOARD_CACHE["total_pages"],
                    "leaderboard": LEADERBOARD_CACHE["data"][:limit],
                }
            ),
            200,
        )

    # Consultar DB ordenando por Elo descendente
    pagination = User.query.order_by(
        User.elo_rating.desc()
    ).paginate(
        page=page,
        per_page=limit,
        error_out=False,
    )

    ranking = []
    start_rank = (page - 1) * limit + 1

    for idx, user in enumerate(pagination.items):
        u_dict = user.to_dict()

        stats = u_dict.get(
            "stats",
            {
                "wins": 0,
                "losses": 0,
                "matches_played": 0,
            },
        )

        total = stats.get("matches_played", 0)
        wins = stats.get("wins", 0)

        win_rate = (
            round((wins / total) * 100, 2)
            if total > 0
            else 0.0
        )

        ranking.append(
            {
                "rank": start_rank + idx,
                "id": str(user.id),
                "username": user.username,
                "elo_rating": user.elo_rating,
                "stats": {
                    "matches_played": total,
                    "wins": wins,
                    "losses": stats.get("losses", 0),
                    "win_rate_percentage": win_rate,
                },
            }
        )

    # Guardar en cache los datos y totales si es la primera página
    if page == 1:
        LEADERBOARD_CACHE["data"] = ranking
        LEADERBOARD_CACHE["total_users"] = pagination.total
        LEADERBOARD_CACHE["total_pages"] = pagination.pages
        LEADERBOARD_CACHE["expires_at"] = now + CACHE_TTL_SECONDS

    return (
        jsonify(
            {
                "source": "database",
                "page": page,
                "limit": limit,
                "total_users": pagination.total,
                "total_pages": pagination.pages,
                "leaderboard": ranking,
            }
        ),
        200,
    )