from .base import Engine
import chess
import chess.engine
import os

from collections.abc import Mapping, Sequence

class ReasonerEngine(Engine):
    """The engine powered by our reasoner."""

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name)
        # init

    def close(self) -> None:
        pass

    def play(self, board: chess.Board) -> chess.Move:
        """Returns the best move from reasoner."""
        # here we would want to prompt the LLM
        # Fallbacks: reprompting if LLM doesn't respond properly

# Example Usage
if __name__ == "__main__":
    engine = ReasonerEngine()

    board = chess.Board()
    print("Best move:", engine.play(board))

    engine.close()

