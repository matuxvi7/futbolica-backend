from src.extensions import db
from src.models import User


def calculate_expected_score(rating_a: int, rating_b: int) -> float:
    """Calcula la probabilidad/expectativa de victoria del jugador A frente al B (0.0 a 1.0)."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def update_match_elo(
    player_a_id: str,
    player_b_id: str,
    result_a: float,  # 1.0 = Victoria A, 0.5 = Empate, 0.0 = Derrota A
    k_factor: int = 32,
) -> dict | None:
    """
    Calcula y aplica la variación de Elo post-partida para ambos jugadores,
    actualizando sus ratings y métricas en PostgreSQL.
    """
    user_a = User.query.get(player_a_id)
    user_b = User.query.get(player_b_id)

    if not user_a or not user_b:
        return None

    expected_a = calculate_expected_score(
        user_a.elo_rating,
        user_b.elo_rating,
    )

    expected_b = calculate_expected_score(
        user_b.elo_rating,
        user_a.elo_rating,
    )

    result_b = 1.0 - result_a

    # Cálculo de variación de Elo
    delta_a = round(k_factor * (result_a - expected_a))
    delta_b = round(k_factor * (result_b - expected_b))

    # Actualizar rating Elo
    old_elo_a = user_a.elo_rating
    old_elo_b = user_b.elo_rating

    user_a.elo_rating += delta_a
    user_b.elo_rating += delta_b

    # Actualizar atributos de estadísticas si existen en el modelo
    for user, result in [(user_a, result_a), (user_b, result_b)]:
        if hasattr(user, "matches_played"):
            user.matches_played = (
                getattr(user, "matches_played", 0) or 0
            ) + 1

        if result == 1.0 and hasattr(user, "wins"):
            user.wins = (getattr(user, "wins", 0) or 0) + 1

        elif result == 0.0 and hasattr(user, "losses"):
            user.losses = (getattr(user, "losses", 0) or 0) + 1

    db.session.commit()

    return {
        "player_a": {
            "id": str(user_a.id),
            "username": user_a.username,
            "old_elo": old_elo_a,
            "new_elo": user_a.elo_rating,
            "change": delta_a,
        },
        "player_b": {
            "id": str(user_b.id),
            "username": user_b.username,
            "old_elo": old_elo_b,
            "new_elo": user_b.elo_rating,
            "change": delta_b,
        },
    }