import time
from typing import Dict, Optional


class MatchState:
    def __init__(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        turn_time_limit: int = 15,
    ):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.turn_time_limit = turn_time_limit  # Segundos por turno
        self.current_turn = player1_id  # Comienza el jugador 1
        self.turn_start_time = time.time()
        self.moves_history = []
        self.status = "active"  # 'active', 'finished', 'timeout'
        self.winner_id = None

    def is_turn_valid(self, player_id: str) -> bool:
        """Verifica si es el turno del jugador y si no se ha agotado el tiempo."""
        if self.status != "active" or self.current_turn != player_id:
            return False

        return (
            time.time() - self.turn_start_time
        ) <= self.turn_time_limit

    def submit_move(self, player_id: str, move_data: dict) -> dict:
        """Registra una jugada y cambia el turno al oponente."""
        if not self.is_turn_valid(player_id):
            return {
                "success": False,
                "reason": "Turno inválido o tiempo agotado",
            }

        next_turn = (
            self.player2_id
            if player_id == self.player1_id
            else self.player1_id
        )

        move_entry = {
            "player_id": player_id,
            "move": move_data,
            "timestamp": time.time(),
        }

        self.moves_history.append(move_entry)

        # Cambiar turno y reiniciar reloj
        self.current_turn = next_turn
        self.turn_start_time = time.time()

        return {
            "success": True,
            "move": move_entry,
            "next_turn": self.current_turn,
            "time_remaining": self.turn_time_limit,
        }

    def get_state(self) -> dict:
        """Devuelve el estado actual de la partida para sincronizar a los clientes."""
        elapsed = time.time() - self.turn_start_time
        time_left = max(0, int(self.turn_time_limit - elapsed))

        return {
            "match_id": self.match_id,
            "current_turn": self.current_turn,
            "time_remaining": time_left,
            "status": self.status,
            "winner_id": self.winner_id,
            "moves_count": len(self.moves_history),
        }


class MatchManagerService:
    def __init__(self):
        self.active_matches: Dict[str, MatchState] = {}

    def create_match(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
    ) -> MatchState:
        match = MatchState(match_id, player1_id, player2_id)
        self.active_matches[match_id] = match

        return match

    def get_match(self, match_id: str) -> Optional[MatchState]:
        return self.active_matches.get(match_id)


match_manager = MatchManagerService()