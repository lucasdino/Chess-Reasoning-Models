import copy
import math
import queue
import chess
import multiprocessing

from utils import get_size
from game import _EVAL_STOCKFISH_ENGINE, _play_game
from engine.base import Engine
from engine.stockfish import StockfishEngine
import torch
import os


def get_size(queue):
    try:
        queue_size = queue.qsize()
    except NotImplementedError:
        queue_size = "Unavailable on macOS"

    return queue_size

def create_stockfish_engine(name: str, elo: int, time: float) -> Engine:
    """Creates a Stockfish engine with a specific Elo rating."""
    engine = StockfishEngine(
        name = name,
        limit=chess.engine.Limit(time=time)
    )
    engine.elo = elo
    return engine

def create_engine(engine_name, time: float | None = None):
    engine_type, elo = engine_name.split("_")
    if engine_type == "Stockfish":
        return create_stockfish_engine(engine_name,elo, time)
    raise KeyError(f"{engine_name} is not supported")
