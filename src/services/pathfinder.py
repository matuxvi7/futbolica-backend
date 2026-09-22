from collections import deque
from uuid import UUID

from src.extensions import db
from src.models import (
    Player,
    Team,
    Coach,
    Competition,
    player_teams,
    player_coaches,
    team_competitions,
)


def get_neighbors(entity_id: UUID, entity_type: str) -> list[dict]:
    """
    Obtiene todos los vecinos inmediatos (nodos conectados)
    de una entidad en el grafo.
    """
    neighbors = []

    if entity_type == "player":
        # 1. Equipos por los que pasó el jugador
        teams = (
            db.session.query(Team)
            .join(player_teams)
            .filter(player_teams.c.player_id == entity_id)
            .all()
        )

        for t in teams:
            neighbors.append(
                {
                    "id": t.id,
                    "type": "team",
                    "name": t.name,
                    "label": f"Club: {t.name}",
                }
            )

        # 2. Entrenadores que lo dirigieron
        coaches = (
            db.session.query(Coach)
            .join(player_coaches)
            .filter(player_coaches.c.player_id == entity_id)
            .all()
        )

        for c in coaches:
            neighbors.append(
                {
                    "id": c.id,
                    "type": "coach",
                    "name": c.name,
                    "label": f"DT: {c.name}",
                }
            )

    elif entity_type == "team":
        # 1. Jugadores que pasaron por el equipo
        players = (
            db.session.query(Player)
            .join(player_teams)
            .filter(player_teams.c.team_id == entity_id)
            .all()
        )

        for p in players:
            neighbors.append(
                {
                    "id": p.id,
                    "type": "player",
                    "name": p.name,
                    "label": f"Jugador: {p.name}",
                }
            )

        # 2. Competiciones disputadas por el equipo
        comps = (
            db.session.query(Competition)
            .join(team_competitions)
            .filter(team_competitions.c.team_id == entity_id)
            .all()
        )

        for c in comps:
            neighbors.append(
                {
                    "id": c.id,
                    "type": "competition",
                    "name": c.name,
                    "label": f"Torneo: {c.name}",
                }
            )

    elif entity_type == "coach":
        # Jugadores dirigidos por el entrenador
        players = (
            db.session.query(Player)
            .join(player_coaches)
            .filter(player_coaches.c.coach_id == entity_id)
            .all()
        )

        for p in players:
            neighbors.append(
                {
                    "id": p.id,
                    "type": "player",
                    "name": p.name,
                    "label": f"Jugador: {p.name}",
                }
            )

    elif entity_type == "competition":
        # Equipos que participaron en la competición
        teams = (
            db.session.query(Team)
            .join(team_competitions)
            .filter(team_competitions.c.competition_id == entity_id)
            .all()
        )

        for t in teams:
            neighbors.append(
                {
                    "id": t.id,
                    "type": "team",
                    "name": t.name,
                    "label": f"Club: {t.name}",
                }
            )

    return neighbors


def find_shortest_path(
    start_id: UUID,
    target_id: UUID,
    start_type: str = "player",
    target_type: str = "player",
) -> dict | None:
    """
    Ejecuta Búsqueda en Anchura (BFS) para hallar la ruta más corta
    entre start_id y target_id.

    Retorna la ruta completa y la distancia en pasos.
    """
    if start_id == target_id and start_type == target_type:
        return {
            "distance": 0,
            "path": [],
        }

    # Cola BFS: almacena tuplas de
    # (id_actual, tipo_actual, camino_recorrido)
    queue = deque([(start_id, start_type, [])])

    visited = {(start_id, start_type)}

    while queue:
        curr_id, curr_type, path = queue.popleft()

        # Explorar vecinos
        for neighbor in get_neighbors(curr_id, curr_type):
            n_id = neighbor["id"]
            n_type = neighbor["type"]

            if (n_id, n_type) in visited:
                continue

            new_path = path + [neighbor]

            # ¿Llegamos al destino?
            if n_id == target_id and n_type == target_type:
                return {
                    "distance": len(new_path),
                    "path": new_path,
                }

            visited.add((n_id, n_type))
            queue.append((n_id, n_type, new_path))

    return None  # No hay conexión entre los nodos