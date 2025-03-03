import itertools
from collections.abc import Mapping, Sequence
from engine.stockfish import StockfishEngine
from engine.base import Engine
import chess
import chess.pgn
import copy
from game import _EVAL_STOCKFISH_ENGINE, _play_game

def _run_tournament(
    unknown_engine: tuple[str, Engine],
    engines: Mapping[str, Engine],
    opening_boards: Sequence[chess.Board],
) -> Sequence[chess.pgn.Game]:
  """Runs a tournament between engines given openings.

  We play both sides for each opening, and the total number of games played per
  pair is therefore 2 * len(opening_boards).

  Args:
    engines: A mapping from engine names to engines.
    opening_boards: The boards to use as openings.

  Returns:
    The games played between all the engines.
  """
  games = list()

  for engine_name in engines:
    engine_name_0 = unknown_engine[0]
    engine_name_1 = engine_name
    print(f'Playing games between {engine_name_0} and {engine_name_1}')
    engine_0 = unknown_engine[1]
    engine_1 = engines[engine_name_1]

    for opening_board, white_idx in itertools.product(opening_boards, (0, 1)):
      white_name = (engine_name_0, engine_name_1)[white_idx]
      game = _play_game(
          engines=(engine_0, engine_1),
          engines_names=(engine_name_0, engine_name_1),
          white_name=white_name,
          # Copy as we modify the opening board in the function.
          initial_board=copy.deepcopy(opening_board),
      )
      print(game.headers["White"], game.headers["Black"], game.headers["Result"])
      games.append(game)

  return games

def create_stockfish_engine(name: str, elo: int, limit: chess.engine.Limit) -> chess.engine.SimpleEngine:
    """Creates a Stockfish engine with a specific Elo rating."""
    engine = StockfishEngine(limit=limit)
    engine.elo = elo
    return engine

def save_games_to_pgn(games: Sequence[chess.pgn.Game], filename: str):
    """Saves the list of games to a .pgn file."""
    with open(filename, "w") as pgn_file:
        for game in games:
            print(game, file=pgn_file, end="\n\n")
    print(f"Saved {len(games)} games to {filename}")

def main():
    # Define engines with different Elo ratings

    known_engine_configs = {
        "Stockfish_1400": 1400,
        "Stockfish_1500": 1500,
        "Stockfish_1600": 1600,
        "Stockfish_1700": 1700,
        "Stockfish_1800": 1800,
        "Stockfish_1900": 1900,
        "Stockfish_2000": 2000,
        "Stockfish_2100": 2100,
        "Stockfish_2200": 2200,
        "Stockfish_2300": 2300,
        "Stockfish_2400": 2400,
        "Stockfish_2500": 2500,
        "Stockfish_2600": 2600,
        "Stockfish_2700": 2700,
        "Stockfish_2800": 2800,
    }

    # Create Stockfish engines
    known_engines = {
        name: create_stockfish_engine(name, elo, limit=chess.engine.Limit(time=0.1)) for name, elo in known_engine_configs.items()
    }

    unknown_engine = ("unknown", create_stockfish_engine("unknown", 1950, limit=chess.engine.Limit(time=0.1)))

    # Define opening positions (start position + a few common openings)
    opening_fens = [
        chess.STARTING_FEN,  # Standard start
        # "rnbqkb1r/pppppppp/7n/8/8/7N/PPPPPPPP/RNBQKB1R w KQkq - 0 1",  # Knight opening
        # "rnbqkb1r/pppp1ppp/5n2/4p3/8/5N2/PPPPPPPP/RNBQKB1R w KQkq e6 0 2",  # Ruy-Lopez-like
    ]
    opening_boards = [chess.Board(fen) for fen in opening_fens]

    # Run the tournament
    games = _run_tournament(unknown_engine, known_engines, opening_boards)

    # Save games to a PGN file
    save_games_to_pgn(games, "tournament_results.pgn")

    # Clean up engines
    for engine in known_engines.values():
        engine.close()
    unknown_engine[1].close()

    _EVAL_STOCKFISH_ENGINE.close()

if __name__ == "__main__":
    main()
