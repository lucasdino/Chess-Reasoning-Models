from .base import Engine
import chess
import chess.engine
import os

from collections.abc import Mapping, Sequence

class StockfishEngine(Engine):
    """The classical version of stockfish."""

    def __init__(
        self,
        name: str,
        limit: chess.engine.Limit,
    ) -> None:
        super().__init__(name)
        self._limit = limit
        self._skill_level = None
        self._elo = None
        stockfish_path = "/opt/homebrew/bin/stockfish" # Update this path if needed
        self._engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def close(self) -> None:
        self._engine.close()

    @property
    def limit(self) -> chess.engine.Limit:
        return self._limit

    @property
    def skill_level(self) -> int | None:
        return self._skill_level
    
    @property
    def elo(self) -> int | None:
        return self._elo

    @skill_level.setter
    def skill_level(self, skill_level: int) -> None:
        self._skill_level = skill_level
        self._engine.configure({'Skill Level': self._skill_level})

    @elo.setter
    def elo(self, elo: int) -> None:
        self._elo = elo
        self._engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})

    def analyse(self, board: chess.Board):
        """Analyzes the position and returns Stockfish's evaluation."""
        analysis = self._engine.analyse(board, limit=self._limit)
        return analysis


    def play(self, board: chess.Board) -> chess.Move:
        """Returns the best move from stockfish."""
        best_move = self._engine.play(board, limit=self._limit).move
        if best_move is None:
            raise ValueError('No best move found, something went wrong.')
        return best_move

# Example Usage
if __name__ == "__main__":
    engine = StockfishEngine(limit=chess.engine.Limit(time=0.05))

    board = chess.Board()
    print("Best move:", engine.play(board))

    analysis = engine.analyse(board)
    print("Position evaluation:", analysis)

    engine.close()

