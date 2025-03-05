from abc import ABC, abstractmethod
import chess

class Engine(ABC):
    @abstractmethod
    def play(self, board: chess.Board) -> chess.Move:
        """Returns the best legal move from a given board."""

    def __init__(self, name):
        self._name = name