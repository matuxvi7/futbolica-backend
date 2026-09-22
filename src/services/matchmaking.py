import time
import uuid
from typing import Dict, Optional, Tuple


class MatchmakingQueue:
    def __init__(
        self,
        initial_tolerance: int = 100,
        expansion_rate: int = 50,
        expansion_interval: int = 5,
    ):
        self.queue: Dict[str, dict] = {}
        self.active_matches: Dict[str, dict] = {}
        # {user_id: match_info}

        self.initial_tolerance = initial_tolerance
        self.expansion_rate = expansion_rate
        self.expansion_interval = expansion_interval

    def add_player(self, user_id: str, username: str, elo: int) -> bool:
        if user_id in self.queue:
            return False

        # Limpiar registro de partida previa si existía
        self.active_matches.pop(user_id, None)

        self.queue[user_id] = {
            "user_id": user_id,
            "username": username,
            "elo": elo,
            "joined_at": time.time(),
        }

        return True

    def remove_player(self, user_id: str) -> bool:
        removed_q = self.queue.pop(user_id, None) is not None
        removed_m = self.active_matches.pop(user_id, None) is not None

        return removed_q or removed_m

    def get_current_tolerance(self, joined_at: float) -> int:
        elapsed_seconds = time.time() - joined_at
        intervals = int(elapsed_seconds // self.expansion_interval)

        return self.initial_tolerance + (
            intervals * self.expansion_rate
        )

    def find_match(
        self,
        user_id: str,
    ) -> Optional[Tuple[dict, dict, str]]:
        # 1. Verificar si el usuario ya fue emparejado previamente
        if user_id in self.active_matches:
            match = self.active_matches[user_id]

            return (
                match["players"][0],
                match["players"][1],
                match["match_id"],
            )

        if user_id not in self.queue:
            return None

        player = self.queue[user_id]
        player_elo = player["elo"]
        player_tolerance = self.get_current_tolerance(
            player["joined_at"]
        )

        for other_id, other_player in list(self.queue.items()):
            if other_id == user_id:
                continue

            other_elo = other_player["elo"]
            other_tolerance = self.get_current_tolerance(
                other_player["joined_at"]
            )

            elo_diff = abs(player_elo - other_elo)

            if (
                elo_diff <= player_tolerance
                or elo_diff <= other_tolerance
            ):
                # Sacar a ambos de la cola de espera
                self.queue.pop(user_id, None)
                self.queue.pop(other_id, None)

                match_id = f"match_{uuid.uuid4().hex[:8]}"

                match_info = {
                    "match_id": match_id,
                    "players": [player, other_player],
                }

                # Registrar la partida activa para que AMBOS jugadores
                # puedan consultarla vía /status
                self.active_matches[user_id] = match_info
                self.active_matches[other_id] = match_info

                return player, other_player, match_id

        return None


matchmaking_service = MatchmakingQueue()