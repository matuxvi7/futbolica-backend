import time
from typing import Dict, Optional

from src.services.elo import update_match_elo


class MatchState:
    def __init__(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        total_rounds: int = 3,
        turn_time_limit: int = 15,
    ):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.total_rounds = total_rounds
        self.turn_time_limit = turn_time_limit  # Segundos por turno

        self.current_round = 1
        self.current_turn = player1_id  # Comienza el jugador 1
        self.turn_start_time = time.time()

        self.moves_history = []
        self.scores = {
            player1_id: 0,
            player2_id: 0,
        }

        self.status = "active"  # 'active', 'finished', 'timeout'
        self.winner_id = None
        self.elo_result = None

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
            "round": self.current_round,
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

    def submit_round_win(self, winning_player_id: str) -> dict:
        """Registra al ganador de la ronda actual y avanza a la siguiente o finaliza el duelo."""
        if self.status != "active":
            return {"status": "already_finished"}

        if winning_player_id in self.scores:
            self.scores[winning_player_id] += 1

        wins_p1 = self.scores[self.player1_id]
        wins_p2 = self.scores[self.player2_id]

        needed_to_win = (self.total_rounds // 2) + 1

        # Verificar si alguien ganó la mayoría de rondas o llegamos al límite
        if (
            wins_p1 >= needed_to_win
            or wins_p2 >= needed_to_win
            or self.current_round >= self.total_rounds
        ):
            self.status = "finished"

            if wins_p1 > wins_p2:
                self.winner_id = self.player1_id
                result_a = 1.0
            elif wins_p2 > wins_p1:
                self.winner_id = self.player2_id
                result_a = 0.0
            else:
                self.winner_id = None  # Empate
                result_a = 0.5

            # Impactar Elo en PostgreSQL usando el servicio BE-11
            self.elo_result = update_match_elo(
                player_a_id=self.player1_id,
                player_b_id=self.player2_id,
                result_a=result_a,
            )

            return {
                "match_status": "finished",
                "winner_id": self.winner_id,
                "final_scores": self.scores,
                "elo_update": self.elo_result,
            }

        # Avanzar a la siguiente ronda
        self.current_round += 1
        self.turn_start_time = time.time()

        return {
            "match_status": "active",
            "current_round": self.current_round,
            "scores": self.scores,
        }

    def get_state(self) -> dict:
        """Devuelve el estado actual de la partida para sincronizar a los clientes."""
        elapsed = time.time() - self.turn_start_time
        time_left = max(0, int(self.turn_time_limit - elapsed))

        return {
            "match_id": self.match_id,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "current_turn": self.current_turn,
            "time_remaining": time_left,
            "scores": self.scores,
            "status": self.status,
            "winner_id": self.winner_id,
            "moves_count": len(self.moves_history),
            "elo_result": self.elo_result,
        }


class MatchManagerService:
    def __init__(self):
        self.active_matches: Dict[str, MatchState] = {}

    def create_match(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        total_rounds: int = 3,
    ) -> MatchState:
        match = MatchState(
            match_id,
            player1_id,
            player2_id,
            total_rounds=total_rounds,
        )

        self.active_matches[match_id] = match

        return match

    def get_match(self, match_id: str) -> Optional[MatchState]:
        return self.active_matches.get(match_id)


match_manager = MatchManagerService()