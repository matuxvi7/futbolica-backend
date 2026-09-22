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


def validate_connection(
    source_id: UUID,
    target_id: UUID,
    source_type: str,
    target_type: str,
) -> dict:
    """
    Valida con autoridad en el servidor si la entidad target (B)
    es un conector directo y válido para la entidad source (A).
    """

    # 1. No se puede seleccionar el mismo nodo
    if source_id == target_id and source_type == target_type:
        return {
            "valid": False,
            "reason": "No puedes seleccionar el mismo nodo actual.",
        }

    # 2. Conexión Jugador <-> Equipo
    if (
        source_type == "player"
        and target_type == "team"
    ) or (
        source_type == "team"
        and target_type == "player"
    ):
        player_id = source_id if source_type == "player" else target_id
        team_id = target_id if source_type == "player" else source_id

        record = (
            db.session.query(player_teams)
            .filter(
                player_teams.c.player_id == player_id,
                player_teams.c.team_id == team_id,
            )
            .first()
        )

        if record:
            player = Player.query.get(player_id)
            team = Team.query.get(team_id)

            return {
                "valid": True,
                "connection_type": "player_team",
                "label": f"{player.name} jugó en {team.name}",
                "details": {
                    "start_year": record.start_year,
                    "end_year": record.end_year,
                },
            }

    # 3. Conexión Jugador <-> Entrenador
    elif (
        source_type == "player"
        and target_type == "coach"
    ) or (
        source_type == "coach"
        and target_type == "player"
    ):
        player_id = source_id if source_type == "player" else target_id
        coach_id = target_id if source_type == "player" else source_id

        record = (
            db.session.query(player_coaches)
            .filter(
                player_coaches.c.player_id == player_id,
                player_coaches.c.coach_id == coach_id,
            )
            .first()
        )

        if record:
            player = Player.query.get(player_id)
            coach = Coach.query.get(coach_id)

            return {
                "valid": True,
                "connection_type": "player_coach",
                "label": f"{coach.name} dirigió a {player.name}",
                "details": {},
            }

    # 4. Conexión Equipo <-> Competición
    elif (
        source_type == "team"
        and target_type == "competition"
    ) or (
        source_type == "competition"
        and target_type == "team"
    ):
        team_id = source_id if source_type == "team" else target_id
        comp_id = target_id if source_type == "team" else source_id

        record = (
            db.session.query(team_competitions)
            .filter(
                team_competitions.c.team_id == team_id,
                team_competitions.c.competition_id == comp_id,
            )
            .first()
        )

        if record:
            team = Team.query.get(team_id)
            comp = Competition.query.get(comp_id)

            return {
                "valid": True,
                "connection_type": "team_competition",
                "label": f"{team.name} disputó {comp.name}",
                "details": {
                    "season": record.season,
                },
            }

    # 5. Conexión directa Jugador <-> Jugador
    # Compañeros con solapamiento de años
    elif source_type == "player" and target_type == "player":
        p1_records = (
            db.session.query(
                player_teams.c.team_id,
                player_teams.c.start_year,
                player_teams.c.end_year,
            )
            .filter(player_teams.c.player_id == source_id)
            .all()
        )

        p1_teams = {
            r.team_id: (r.start_year, r.end_year)
            for r in p1_records
        }

        p2_records = (
            db.session.query(
                player_teams.c.team_id,
                player_teams.c.start_year,
                player_teams.c.end_year,
            )
            .filter(
                player_teams.c.player_id == target_id,
                player_teams.c.team_id.in_(p1_teams.keys()),
            )
            .all()
        )

        for team_id, p2_start, p2_end in p2_records:
            p1_start, p1_end = p1_teams[team_id]

            if (
                p1_start is None
                or p2_start is None
                or (p1_start <= p2_end and p2_start <= p1_end)
            ):
                p1 = Player.query.get(source_id)
                p2 = Player.query.get(target_id)
                team = Team.query.get(team_id)

                return {
                    "valid": True,
                    "connection_type": "teammates",
                    "label": (
                        f"{p1.name} y {p2.name} "
                        f"fueron compañeros en {team.name}"
                    ),
                    "details": {
                        "team": team.name,
                    },
                }

    return {
        "valid": False,
        "reason": (
            "No existe conexión directa entre "
            "las entidades seleccionadas."
        ),
    }