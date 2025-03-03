import chess
import chess.svg
from IPython.display import SVG, display


def visualize_board_ipynb(fen_string: str, size: int = 600) -> None:
    """ Visualizes a chess board using SVG with a customizable size. """
    board = chess.Board(fen_string)
    display(SVG(chess.svg.board(board, size=size)))


def print_top_moves(legal_moves: list, win_probabilities: list, top_n: int = None) -> None:
    """
    Prints a nicely formatted table of moves sorted by win probability.

    Args:
        legal_moves (list): List of legal moves.
        win_probabilities (list): Corresponding list of win probabilities.
        top_n (int, optional): Number of top moves to display. If None, displays all.
    """
    # Zip and sort moves by win probability (descending order)
    sorted_moves = sorted(zip(legal_moves, win_probabilities), key=lambda x: x[1], reverse=True)
    
    # If top_n is specified, limit the number of displayed moves
    if top_n is not None:
        sorted_moves = sorted_moves[:top_n]

    # Print header and rows
    print(f"{'='*25}\n|   Move   |  Win Prob  |\n{'-'*25}")
    
    # Print rows
    for move, prob in sorted_moves:
        print(f"|   {move:<5}  |   {prob:.4f}   |")