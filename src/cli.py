import click

from flask import Flask


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command():
        """Puebla la base de datos con datos de prueba."""

        from src.seeds import seed_db

        seed_db()

    @app.cli.command("test-path")
    def test_path_command():
        """Prueba el algoritmo BFS entre Messi y Falcao."""

        from src.models import Player
        from src.services.pathfinder import find_shortest_path

        messi = Player.query.filter_by(name="Lionel Messi").first()
        falcao = Player.query.filter_by(name="Radamel Falcao").first()

        if not messi or not falcao:
            print("❌ Ejecuta 'flask seed' primero para cargar datos.")
            return

        print(
            f"🔍 Buscando ruta entre "
            f"{messi.name} y {falcao.name}..."
        )

        result = find_shortest_path(
            messi.id,
            falcao.id,
            "player",
            "player",
        )

        if result:
            print(
                f"✅ ¡Ruta encontrada! "
                f"Distancia: {result['distance']} pasos."
            )

            for step in result["path"]:
                print(f"   ➡️ {step['label']}")
        else:
            print("❌ No se encontró camino.")