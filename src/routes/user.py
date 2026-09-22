from flask import Blueprint, jsonify

from src.models import User
from src.utils.decorators import token_required


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/api/v1/users",
)


@user_bp.route("/me", methods=["GET"])
@token_required
def get_current_user_profile(current_user: User):
    """Devuelve la información del usuario autenticado."""
    return (
        jsonify(
            {
                "message": "Perfil obtenido con éxito",
                "user": current_user.to_dict(),
            }
        ),
        200,
    )


@user_bp.route("/<user_id>", methods=["GET"])
def get_public_user_profile(user_id):
    """Devuelve el perfil público y las estadísticas calculadas de cualquier usuario."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Extraer stats desde to_dict() para evitar AttributeError
    user_dict = user.to_dict()

    stats = user_dict.get(
        "stats",
        {
            "wins": 0,
            "losses": 0,
            "matches_played": 0,
        },
    )

    total_matches = stats.get("matches_played", 0)
    wins = stats.get("wins", 0)

    win_rate = (
        round((wins / total_matches) * 100, 2)
        if total_matches > 0
        else 0.0
    )

    return (
        jsonify(
            {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "elo_rating": user.elo_rating,
                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    ),
                    "stats": {
                        "matches_played": total_matches,
                        "wins": wins,
                        "losses": stats.get("losses", 0),
                        "win_rate_percentage": win_rate,
                    },
                }
            }
        ),
        200,
    )