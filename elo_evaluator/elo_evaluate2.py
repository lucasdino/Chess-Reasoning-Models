import copy
import itertools
from engine.base import Engine
from engine.stockfish import StockfishEngine
import chess
import math
import chess.pgn
from collections.abc import Mapping, Sequence

from game import _play_game, _EVAL_STOCKFISH_ENGINE


def create_stockfish_engine(name: str, elo: int, limit: chess.engine.Limit) -> chess.engine.SimpleEngine:
    """Creates a Stockfish engine with a specific Elo rating."""
    engine = StockfishEngine(limit=limit)
    engine.elo = elo
    return engine

def estimate_elo(winrate, known_elo):
    """Calculates the estimated Elo rating based on winrate against a known opponent."""
    if winrate in [0, 1]:  # Prevent log(0) issues
        winrate = max(min(winrate, 0.99), 0.01)
    return known_elo - 400 * math.log10((1 - winrate) / winrate)

def _play_series(
    known_engine: tuple[str, Engine],
    unknown_engine: tuple[str, Engine],
    opening_boards: Sequence[chess.Board],
    num_games: int,
) -> tuple[int, int, int]: #(win, draw, loss) for unknown engine
    print(f"Playing series between {known_engine[0]} and {unknown_engine[0]}")
    wins, draws, losses = 0, 0, 0
    
    num_openings = len(opening_boards)
    games_per_opening = num_games // num_openings
    remaining_games = num_games % num_openings
    
    engines = (known_engine[1], unknown_engine[1])
    engines_names = (known_engine[0], unknown_engine[0])
    
    game_results = []
    
    for i, board in enumerate(opening_boards):
        games_to_play = games_per_opening + (1 if i < remaining_games else 0)
        
        for j in range(games_to_play // 2):
            game = _play_game(engines, engines_names, white_name=unknown_engine[0], initial_board=copy.deepcopy(board))
            game_results.append(game)
            
            game = _play_game(engines, engines_names, white_name=known_engine[0], initial_board=copy.deepcopy(board))
            game_results.append(game)
    
    for game in game_results:
        result = game.headers.get("Result", "*")
        if result == "1-0":  # White wins
            if game.headers["White"] == unknown_engine[0]:
                wins += 1
            else:
                losses += 1
        elif result == "0-1":  # Black wins
            if game.headers["Black"] == unknown_engine[0]:
                wins += 1
            else:
                losses += 1
        else:  # Draw
            draws += 1
    
    return wins, draws, losses

def main():
    NUM_GAMES = 10  # Number of games per opponent
    TIME_LIMIT = 0.01
    KNOWN_ENGINES_CONFIGS = {
        "Stockfish_1400": 1400,
        "Stockfish_1600": 1600,
        "Stockfish_1800": 1800,
        "Stockfish_2000": 2000,
        "Stockfish_2200": 2200,
        "Stockfish_2400": 2400,
        "Stockfish_2600": 2600,
        "Stockfish_2800": 2800,
    }
    unknown_engine = ("unknown", create_stockfish_engine("unknown", 1950, limit=chess.engine.Limit(time=TIME_LIMIT)))
    known_engines = {
        name: create_stockfish_engine(name, elo, limit=chess.engine.Limit(time=TIME_LIMIT)) for name, elo in KNOWN_ENGINES_CONFIGS.items()
    }
    winrates = {opponent: 0 for opponent in KNOWN_ENGINES_CONFIGS}
    opening_fens = [
        chess.STARTING_FEN,  # Standard start
        # "rnbqkb1r/pppppppp/7n/8/8/7N/PPPPPPPP/RNBQKB1R w KQkq - 0 1",  # Knight opening
        # "rnbqkb1r/pppp1ppp/5n2/4p3/8/5N2/PPPPPPPP/RNBQKB1R w KQkq e6 0 2",  # Ruy-Lopez-like
    ]
    opening_boards = [chess.Board(fen) for fen in opening_fens]

    # Play series against each known engine
    for name, engine in known_engines.items():
        wins, draws, losses = _play_series((name, engine), unknown_engine, opening_boards, NUM_GAMES)
        winrates[name] = (wins + 0.5 * draws) / NUM_GAMES

    # Compute estimated Elo for each opponent
    elo_estimates = [estimate_elo(winrates[opponent], opp_elo) for opponent, opp_elo in KNOWN_ENGINES_CONFIGS.items()]

    # Average Elo estimate
    average_elo = sum(elo_estimates) / len(elo_estimates)

    # Results
    print("Winrates:", winrates)
    print("Elo Estimates:", elo_estimates)
    print("Average Estimated Elo:", round(average_elo, 2))

    # Clean up engines
    for engine in known_engines.values():
        engine.close()
    unknown_engine[1].close()
    _EVAL_STOCKFISH_ENGINE.close()

if __name__ == "__main__":
    main()