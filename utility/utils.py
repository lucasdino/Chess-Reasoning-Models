import random
import chess

def get_random_piece_and_position(board: str):
    """
    Selects a random unique piece from the given FEN board representation and returns its piece letter and position.

    This function first identifies all unique piece types on the board and selects one at random.
    Then, it picks a random position where that piece is located.

    Args:
        board (str): A string representing the chessboard in Forsyth-Edwards Notation (FEN).

    Returns:
        tuple: (piece_letter, position) where:
            - piece_letter (str): The letter representing the selected chess piece (e.g., 'N' for knight, 'p' for pawn).
            - position (str): The corresponding board position in algebraic notation (e.g., 'e4').
    """
    files = 'abcdefgh'
    ranks = '87654321'  # FEN starts from rank 8 (top) to rank 1 (bottom)
    
    # Extract board part from FEN
    board_rows = board.split()[0].split('/')
    
    piece_positions = {}  # Map piece -> list of positions
    
    for rank_index, row in enumerate(board_rows):
        file_index = 0
        for char in row:
            if char.isdigit():
                file_index += int(char)  # Skip empty squares
            else:
                position = files[file_index] + ranks[rank_index]  # Convert to algebraic notation
                if char not in piece_positions:
                    piece_positions[char] = []
                piece_positions[char].append(position)
                file_index += 1  # Move to the next file

    # Select a random unique piece type
    if not piece_positions:
        return None, None

    random_piece = random.choice(list(piece_positions.keys()))  # Choose a unique piece
    random_position = random.choice(piece_positions[random_piece])  # Choose a random position of that piece
    
    return random_piece, random_position


def get_legal_moves(fen: str, piece_position: str, move_representation: str = "UCI") -> list:
    """
    Given a FEN string, the position of a piece, and the desired move representation,
    return the list of legal moves for that piece in the specified format.

    Args:
        fen (str): The current board state in FEN format.
        piece_position (str): The position of the piece (e.g., "e2").
        move_representation (str): The format for representing moves. Can be "UCI" (default), "PGN", etc.

    Returns:
        list: A list of legal moves for the piece at the given position in the requested format.
    """
    # Create a chess board object from the FEN string
    board = chess.Board(fen)
    
    # Get the square corresponding to the piece's position
    square = chess.parse_square(piece_position)
    
    # Get the piece at the given position
    piece = board.piece_at(square)
    
    # If there is no piece at the given position, return an empty list
    if not piece:
        return []

    # Get the legal moves for the piece at the given position
    legal_moves = board.legal_moves

    # Filter moves that start from the given piece position
    legal_moves_for_piece = [move for move in legal_moves if move.from_square == square]

    # Convert the legal moves to the requested format
    if move_representation == "UCI":
        legal_moves_for_piece = [move.uci() for move in legal_moves_for_piece]
    elif move_representation == "PGN":
        legal_moves_for_piece = [move.pgn() for move in legal_moves_for_piece]
    else:
        raise ValueError("Unsupported move representation. Use 'UCI' or 'PGN'.")

    return legal_moves_for_piece

def compare_moves_and_legal_moves(moves, legal_moves):
    # Convert both lists to sets for set operations
    moves_set = set(moves)
    legal_moves_set = set(legal_moves)

    # Correct Moves Predicted: moves that are legal but not predicted
    correct_moves = legal_moves_set - moves_set

    # Illegal Moves Predicted: moves that are predicted but not legal
    illegal_moves = moves_set - legal_moves_set

    # Return the results
    return correct_moves, illegal_moves