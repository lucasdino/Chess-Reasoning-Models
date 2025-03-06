import multiprocessing

import chat
from .base import Engine
import chess
import chess.engine
import os

from collections.abc import Mapping, Sequence
import torch


class DeepseekEngine(Engine):
    """The engine powered by Deepseek."""

    def __init__(
        self,
        name: str,
        model_name: str,
        timeout: int,
    ) -> None:
        super().__init__(name)
        self.session = chat.OllamaSession(model=model_name, use_cuda=False)
        self.timeout = timeout

    def close(self) -> None:
        pass

    def play(self, board: chess.Board) -> chess.Move:
        """Returns the best move from reasoner."""
        # here we would want to prompt the LLM
        fen = board.fen()  # Convert board to FEN string
        legal_moves = [move.uci() for move in board.legal_moves]  # Get all legal moves in UCI format
        print(legal_moves)

        prompt = chat.format_prompt(fen, legal_moves)  # Pass FEN and legal moves list
        print(prompt)
        response, runtime_results = self.session.chat(user_prompt=prompt, timeout=self.timeout)
        print(response)
        move_uci = chat.extract_answer(response)
        move = chess.Move.from_uci(move_uci)
        print(move)
        if move_uci not in legal_moves:
            print("ILLEGAL!")
            # raise chat.IllegalMoveError(f"Model predicted illegal move: {move}")
        return move
        # Fallbacks: reprompting if LLM doesn't respond properly

# Example Usage
if __name__ == "__main__":
    engine = DeepseekEngine(
        name="Deepseek",
        model_name="deepseek-r1:1.5b",
        timeout=30,
    )

    board = chess.Board()
    print("Best move:", engine.play(board))

    engine.close()

