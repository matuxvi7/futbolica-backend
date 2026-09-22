import uuid

from src.extensions import db
from src.models import (
    Player,
    Team,
    Coach,
    Competition,
    User,
    player_teams,
    player_coaches,
    team_competitions,
)


def seed_db():
    """Puebla la base de datos con nodos y conexiones del grafo futbolístico de prueba."""

    print("🌱 Limpiando datos anteriores...")

    db.session.execute(player_coaches.delete())
    db.session.execute(player_teams.delete())
    db.session.execute(team_competitions.delete())

    Player.query.delete()
    Team.query.delete()
    Coach.query.delete()
    Competition.query.delete()
    User.query.delete()

    db.session.commit()

    print("⚽ Insertando clubes...")

    barcelona = Team(
        name="FC Barcelona",
        country="España",
        logo_url="https://example.com/barca.png",
    )

    real_madrid = Team(
        name="Real Madrid",
        country="España",
        logo_url="https://example.com/real.png",
    )

    psg = Team(
        name="Paris Saint-Germain",
        country="Francia",
        logo_url="https://example.com/psg.png",
    )

    man_utd = Team(
        name="Manchester United",
        country="Inglaterra",
        logo_url="https://example.com/utd.png",
    )

    inter_miami = Team(
        name="Inter Miami",
        country="EEUU",
        logo_url="https://example.com/miami.png",
    )

    benfica = Team(
        name="SL Benfica",
        country="Portugal",
        logo_url="https://example.com/benfica.png",
    )

    db.session.add_all(
        [
            barcelona,
            real_madrid,
            psg,
            man_utd,
            inter_miami,
            benfica,
        ]
    )

    db.session.commit()

    print("🏃 Insertando jugadores...")

    messi = Player(
        name="Lionel Messi",
        nationality="Argentina",
        position="Delantero",
    )

    di_maria = Player(
        name="Ángel Di María",
        nationality="Argentina",
        position="Extremo",
    )

    ronaldo = Player(
        name="Cristiano Ronaldo",
        nationality="Portugal",
        position="Delantero",
    )

    falcao = Player(
        name="Radamel Falcao",
        nationality="Colombia",
        position="Delantero",
    )

    db.session.add_all(
        [
            messi,
            di_maria,
            ronaldo,
            falcao,
        ]
    )

    db.session.commit()

    print("🔗 Insertando conexiones del grafo (player_teams)...")

    connections = [
        # Lionel Messi
        {
            "player_id": messi.id,
            "team_id": barcelona.id,
            "start_year": 2004,
            "end_year": 2021,
        },
        {
            "player_id": messi.id,
            "team_id": psg.id,
            "start_year": 2021,
            "end_year": 2023,
        },
        {
            "player_id": messi.id,
            "team_id": inter_miami.id,
            "start_year": 2023,
            "end_year": 2026,
        },

        # Ángel Di María
        # Coincide con Messi en PSG y con Ronaldo en Real Madrid
        {
            "player_id": di_maria.id,
            "team_id": benfica.id,
            "start_year": 2007,
            "end_year": 2010,
        },
        {
            "player_id": di_maria.id,
            "team_id": real_madrid.id,
            "start_year": 2010,
            "end_year": 2014,
        },
        {
            "player_id": di_maria.id,
            "team_id": man_utd.id,
            "start_year": 2014,
            "end_year": 2015,
        },
        {
            "player_id": di_maria.id,
            "team_id": psg.id,
            "start_year": 2015,
            "end_year": 2022,
        },

        # Cristiano Ronaldo
        {
            "player_id": ronaldo.id,
            "team_id": man_utd.id,
            "start_year": 2003,
            "end_year": 2009,
        },
        {
            "player_id": ronaldo.id,
            "team_id": real_madrid.id,
            "start_year": 2009,
            "end_year": 2018,
        },

        # Radamel Falcao
        # Coincide con Di María y Ronaldo en Man Utd
        {
            "player_id": falcao.id,
            "team_id": man_utd.id,
            "start_year": 2014,
            "end_year": 2015,
        },
    ]

    for conn in connections:
        stmt = player_teams.insert().values(
            id=uuid.uuid4(),
            player_id=conn["player_id"],
            team_id=conn["team_id"],
            start_year=conn["start_year"],
            end_year=conn["end_year"],
        )

        db.session.execute(stmt)

    print("👤 Insertando usuario de prueba...")

    demo_user = User(
        username="tester_conector",
        email="test@futbolica.com",
        password_hash="pbkdf2:sha256:demo_password_hash",
        elo_rating=1200,
    )

    db.session.add(demo_user)
    db.session.commit()

    print("✅ Base de datos poblada con éxito.")
