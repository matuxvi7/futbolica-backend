import random

from src.models import Player, Team
from src.services.pathfinder import find_shortest_path


def generate_match_puzzle(
    entity_type: str = "player",
    min_distance: int = 3,
    max_distance: int = 5,
    max_attempts: int = 50,
) -> dict | None:
    """
    Selecciona dinámicamente un par de nodos origen/destino cuyo
    camino más corto se encuentre dentro del rango de dificultad
    deseado (min_distance a max_distance).
    """

    if entity_type == "player":
        candidates = Player.query.all()
    elif entity_type == "team":
        candidates = Team.query.all()
    else:
        candidates = Player.query.all()

    if len(candidates) < 2:
        return None

    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        # Seleccionar dos entidades distintas al azar
        start_node, target_node = random.sample(candidates, 2)

        # Calcular el camino más corto entre ambos
        path_result = find_shortest_path(
            start_node.id,
            target_node.id,
            start_type=entity_type,
            target_type=entity_type,
        )

        if not path_result:
            continue

        distance = path_result["distance"]

        # Verificar si la distancia se ajusta al rango de dificultad
        if min_distance <= distance <= max_distance:
            return {
                "puzzle_id": (
                    f"puz_{start_node.id.hex[:6]}_"
                    f"{target_node.id.hex[:6]}"
                ),
                "difficulty": (
                    "medium" if distance in (3, 4) else "hard"
                ),
                "start_node": {
                    "id": str(start_node.id),
                    "name": start_node.name,
                    "type": entity_type,
                },
                "target_node": {
                    "id": str(target_node.id),
                    "name": target_node.name,
                    "type": entity_type,
                },
                "optimal_distance": distance,
                "solution_path": path_result["path"],
                "attempts_count": attempts,
            }

    # Si con los parámetros estrictos no encuentra en max_attempts,
    # utiliza un par de nodos como fallback.
    start_node, target_node = candidates[0], candidates[-1]

    path_result = find_shortest_path(
        start_node.id,
        target_node.id,
        entity_type,
        entity_type,
    )

    if path_result:
        return {
            "puzzle_id": (
                f"puz_fallback_{start_node.id.hex[:6]}"
            ),
            "difficulty": "easy",
            "start_node": {
                "id": str(start_node.id),
                "name": start_node.name,
                "type": entity_type,
            },
            "target_node": {
                "id": str(target_node.id),
                "name": target_node.name,
                "type": entity_type,
            },
            "optimal_distance": path_result["distance"],
            "solution_path": path_result["path"],
            "attempts_count": attempts,
        }

    return None