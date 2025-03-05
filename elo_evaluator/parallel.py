import copy
import math
import queue
import chess
import multiprocessing

from game import _EVAL_STOCKFISH_ENGINE, _play_game
from engine.base import Engine
from engine.stockfish import StockfishEngine

# Constants
NUM_GAMES = 4  # Total games per ELO level
TIME_LIMIT = 0.01
NUM_WORKERS = 8  # Number of parallel games (each worker uses a GPU core)
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

# Opening positions
opening_fens = [
    chess.STARTING_FEN,  # Standard start
]
opening_boards = [chess.Board(fen) for fen in opening_fens]


def get_size(queue):
    try:
        queue_size = queue.qsize()
    except NotImplementedError:
        queue_size = "Unavailable on macOS"

    return queue_size

def estimate_elo(winrate, known_elo):
    """Estimate ELO based on win rate."""
    if winrate in [0, 1]:  # Prevent log(0) issues
        winrate = max(min(winrate, 0.99), 0.01)
    return known_elo - 400 * math.log10((1 - winrate) / winrate)

def create_stockfish_engine(name: str, elo: int) -> Engine:
    """Creates a Stockfish engine with a specific Elo rating."""
    engine = StockfishEngine(
        name = name,
        limit=chess.engine.Limit(time=TIME_LIMIT)
    )
    engine.elo = elo
    return engine

def create_engine(engine_name):
    engine_type, elo = engine_name.split("_")
    if engine_type == "Stockfish":
        return create_stockfish_engine(engine_name,elo)
    raise KeyError(f"{engine_name} is not supported")

def worker(game_queue, log_lock, log_file, results, results_lock, core_id):
    unknown_engine = create_engine("Stockfish_1950") # replace with LLM
    unknown_engine_name = "unknown"
    while True:
        try:
            known_engine_name, board, is_llm_white = game_queue.get(timeout=1)  # Timeout to prevent deadlocks
            
            game_log_entry = f"Playing game with {known_engine_name}, LLM as White: {is_llm_white}\n"
            queue_size_log_entry = f"Games in Queue: {get_size(game_queue)}\n"
            print(game_log_entry)
            print(queue_size_log_entry)
            with log_lock:
                with open(log_file, "a") as f:
                    f.write(game_log_entry)
                    f.write(queue_size_log_entry)

            known_engine = create_engine(known_engine_name)
            
            game = _play_game(
                (known_engine, unknown_engine),
                (known_engine_name, unknown_engine_name),
                white_name=unknown_engine_name if is_llm_white else known_engine_name,
                initial_board=copy.deepcopy(board),
            )

            known_engine.close()

            # Store result
            result = game.headers.get("Result", "*")
            if result == "1-0":  # White wins
                winner = game.headers["White"]
            elif result == "0-1":  # Black wins
                winner = game.headers["Black"]
            else:
                winner = "draw"

            game_result_log = f"Result: {result} | Winner: {winner} | With: {known_engine_name} | LLM as White: {is_llm_white}\n"
            print(game_result_log)
            with log_lock:
                with open(log_file, "a") as f:
                    f.write(game_result_log)

            # Update results dictionary
            with results_lock:  # Ensure atomic update
                result_keys = {
                    "wins": f"{known_engine_name}_wins",
                    "draws": f"{known_engine_name}_draws",
                    "losses": f"{known_engine_name}_losses",
                }
                for result_key in result_keys.values():
                    if result_key not in results:
                        results[result_key] = 0
                
                if winner == unknown_engine_name:
                    results[result_keys["wins"]] += 1
                elif winner == "draw":
                    results[result_keys["draws"]] += 1
                else:
                    results[result_keys["losses"]] += 1

            
        except queue.Empty:
            _EVAL_STOCKFISH_ENGINE.close()
            unknown_engine.close() # for LLM
            break

    

if __name__ == "__main__":
    results = multiprocessing.Manager().dict()
    # Create game queue
    game_queue = multiprocessing.Queue()
    results_lock = multiprocessing.Lock()
    log_lock = multiprocessing.Lock()
    log_file = "game_log.txt"
    with open("game_log.txt", "w") as file:
        pass  # File is now empty

    # Distribute games evenly among openings
    games_per_opening = NUM_GAMES // len(opening_boards)
    remaining_games = NUM_GAMES % len(opening_boards)

    for i, board in enumerate(opening_boards):
        games_to_play = games_per_opening + (1 if i < remaining_games else 0)
        for stockfish_name, stockfish_engine in KNOWN_ENGINES_CONFIGS.items():
            for _ in range(games_to_play // 2):
                game_queue.put((stockfish_name, board, True))  # LLM as white
                game_queue.put((stockfish_name, board, False))  # LLM as black)

    print("All games added to Queue")

    # Create workers
    processes = []
    for i in range(NUM_WORKERS):  # parallel workers
        core_id = i # TO CHANGE
        p = multiprocessing.Process(target=worker, args=(game_queue, log_lock, log_file, results, results_lock, core_id))
        p.start()
        processes.append(p)

    # # Monitor which processes are still running
    # while any(p.is_alive() for p in processes):
    #     waiting = [p.pid for p in processes if p.is_alive()]
    #     print(f"Still waiting for processes: {waiting}")
    #     time.sleep(1)  # Check periodically

    # Wait for all games to complete
    for p in processes:
        p.join()
    
    _EVAL_STOCKFISH_ENGINE.close()

    print('All games have been played!')
    print(results)
    winrates = {}

    for engine in set(k.split("_")[0] + "_" + k.split("_")[1] for k in results.keys()):
        wins = results.get(f"{engine}_wins", 0)
        draws = results.get(f"{engine}_draws", 0)
        losses = results.get(f"{engine}_losses", 0)

        total_games = wins + draws + losses
        if total_games == 0:
            winrates[engine] = 0
        else:
            winrates[engine] = (wins + 0.5 * draws) / total_games

    # Compute estimated Elo for each opponent
    elo_estimates = {
        opponent: estimate_elo(winrates[opponent], opp_elo)
        for opponent, opp_elo in KNOWN_ENGINES_CONFIGS.items()
    }

    # Compute the average estimated Elo
    average_elo = sum(elo_estimates.values()) / len(elo_estimates)

    # Print results
    print("Winrates:", dict(winrates))
    print("Elo Estimates:", elo_estimates)  # Dictionary format
    print("Average Estimated Elo:", round(average_elo, 2))
