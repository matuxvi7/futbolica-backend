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

    @app.cli.command("validate-step")
    def validate_step_command():
        """Prueba la validación paso a paso de conexiones."""

        from src.models import Player, Team
        from src.services.validator import validate_connection

        messi = Player.query.filter_by(name="Lionel Messi").first()
        di_maria = Player.query.filter_by(name="Ángel Di María").first()
        psg = Team.query.filter_by(name="Paris Saint-Germain").first()
        barca = Team.query.filter_by(name="FC Barcelona").first()
        falcao = Player.query.filter_by(name="Radamel Falcao").first()

        if not messi or not di_maria or not psg or not falcao:
            print("❌ Ejecuta 'flask seed' primero.")
            return

        print("--- PRUEBAS DE VALIDACIÓN ---")

        # 1. Prueba válida: Messi -> PSG
        res1 = validate_connection(
            messi.id,
            psg.id,
            "player",
            "team",
        )

        print(
            f"1. Messi ➡️ PSG: "
            f"{'✅ VÁLIDO' if res1['valid'] else '❌ INVÁLIDO'} "
            f"({res1.get('label') or res1.get('reason')})"
        )

        # 2. Prueba válida: Messi -> Di María (Compañeros en PSG)
        res2 = validate_connection(
            messi.id,
            di_maria.id,
            "player",
            "player",
        )

        print(
            f"2. Messi ➡️ Di María: "
            f"{'✅ VÁLIDO' if res2['valid'] else '❌ INVÁLIDO'} "
            f"({res2.get('label') or res2.get('reason')})"
        )

        # 3. Prueba inválida: Messi -> Falcao
        # No fueron compañeros directos
        res3 = validate_connection(
            messi.id,
            falcao.id,
            "player",
            "player",
        )

        print(
            f"3. Messi ➡️ Falcao: "
            f"{'✅ VÁLIDO' if res3['valid'] else '❌ INVÁLIDO'} "
            f"({res3.get('label') or res3.get('reason')})"
        )

    @app.cli.command("generate-puzzle")
    def generate_puzzle_command():
        """Genera y muestra un enigma dinámico con rango de dificultad."""

        from src.services.puzzle_generator import generate_match_puzzle

        print("🎲 Generando enigma dinámico para partida 1v1...")

        puzzle = generate_match_puzzle(
            entity_type="player",
            min_distance=2,
            max_distance=5,
        )

        if puzzle:
            print("✅ ¡Enigma generado con éxito!")
            print(f"   ID Enigma: {puzzle['puzzle_id']}")
            print(f"   Dificultad: {puzzle['difficulty'].upper()}")
            print(f"   Origen: 🟢 {puzzle['start_node']['name']}")
            print(f"   Destino: 🔴 {puzzle['target_node']['name']}")
            print(
                f"   Distancia óptima: "
                f"{puzzle['optimal_distance']} pasos"
            )

            print("   Solución esperada:")

            for step in puzzle["solution_path"]:
                print(f"      ➡️ {step['label']}")

        else:
            print(
                "❌ No se pudo generar un enigma "
                "con los candidatos actuales."
            )