import chess.pgn
import math

# Constants
eloAdvantage = 32.8  # Advantage of playing first
eloDraw = 97.3  # Likelihood of a draw

def parse_pgn(pgn_file):
    with open(pgn_file, "r") as f:
        games = []
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games.append(game)
    return games

def f(delta):
    """Computes the probability of a win based on Elo difference"""
    return 1 / (1 + 10 ** (delta / 400))

def calculate_probabilities(elo_white, elo_black):
    """Calculates the win, loss, and draw probabilities between two engines"""
    # Calculating the differences with eloAdvantage and eloDraw adjustments
    white_wins_prob = f(elo_black - elo_white - eloAdvantage + eloDraw)
    black_wins_prob = f(elo_white - elo_black + eloAdvantage + eloDraw)
    draw_prob = 1 - white_wins_prob - black_wins_prob
    return white_wins_prob, black_wins_prob, draw_prob

def bayesian_update(unknown_engine, known_ratings, pgn_file):
    """Performs Bayesian Elo updates based on the PGN file"""
    unknown_elo = 0 # what should we put here?

    # Read PGN results and update ratings
    games = parse_pgn(pgn_file)

    for game in games:
        white_engine = game.headers["White"]
        black_engine = game.headers["Black"]
        result = game.headers["Result"]
        print(white_engine, black_engine, result)

        # Calculate the win, loss, and draw probabilities
        if white_engine == unknown_engine:
            # White engine is the unknown one
            black_elo = known_ratings[black_engine]
            white_wins_prob, black_wins_prob, draw_prob = calculate_probabilities(unknown_elo, black_elo)

            if result == "1-0":
                game_result = 1  # White wins
                posterior_elo = unknown_elo + 32 * (game_result - white_wins_prob)
            elif result == "0-1":
                game_result = 0  # Black wins
                posterior_elo = unknown_elo + 32 * (game_result - black_wins_prob)
            else:
                game_result = 0.5  # Draw
                posterior_elo = unknown_elo + 32 * (game_result - draw_prob)

            # Update the unknown engine's Elo
            unknown_elo = posterior_elo
            known_ratings[white_engine] = unknown_elo  # Store the updated Elo

        elif black_engine == unknown_engine:
            # Black engine is the unknown one
            white_elo = known_ratings[white_engine]
            white_wins_prob, black_wins_prob, draw_prob = calculate_probabilities(white_elo, unknown_elo)

            if result == "1-0":
                game_result = 0  # White wins
                posterior_elo = unknown_elo + 32 * (game_result - white_wins_prob)
            elif result == "0-1":
                game_result = 1  # Black wins
                posterior_elo = unknown_elo + 32 * (game_result - black_wins_prob)
            else:
                game_result = 0.5  # Draw
                posterior_elo = unknown_elo + 32 * (game_result - draw_prob)

            # Update the unknown engine's Elo
            unknown_elo = posterior_elo
            known_ratings[black_engine] = unknown_elo  # Store the updated Elo

    return unknown_elo

known_ratings = {
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
unknown_engine = "unknown"

pgn_file = "tournament_results.pgn"
predicted_elo = bayesian_update(unknown_engine, known_ratings, pgn_file)
print(f"Predicted Elo for the unknown engine: {predicted_elo}")