import random
import chess

def get_random_piece_and_position(board: str):
    """
    Selects a random unique piece from the given FEN board representation that belongs to the current player.

    This function first identifies all unique piece types of the current player's color and selects one at random.
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
    
    # Extract board part and turn information from FEN
    board_parts = board.split()
    board_rows = board_parts[0].split('/')
    current_turn = board_parts[1]  # 'w' for white, 'b' for black
    
    piece_positions = {}  # Map piece -> list of positions
    
    for rank_index, row in enumerate(board_rows):
        file_index = 0
        for char in row:
            if char.isdigit():
                file_index += int(char)  # Skip empty squares
            else:
                position = files[file_index] + ranks[rank_index]  # Convert to algebraic notation
                is_white = char.isupper()
                if (current_turn == 'w' and is_white) or (current_turn == 'b' and not is_white):
                    if char not in piece_positions:
                        piece_positions[char] = []
                    piece_positions[char].append(position)
                file_index += 1  # Move to the next file

    # Select a random unique piece type from the current player's pieces
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
        legal_moves_for_piece = [board.san(move) for move in legal_moves_for_piece]
    else:
        raise ValueError("Unsupported move representation. Use 'UCI' or 'PGN'.")

    return legal_moves_for_piece

def compare_moves_and_legal_moves(moves, legal_moves):
    # Convert both lists to sets for set operations
    moves_set = set(moves)
    legal_moves_set = set(legal_moves)

    # Correct Moves Predicted: moves that are legal and predicted
    correct_moves = moves_set & legal_moves_set
    
    # Missed Moves: moves that are legal but not predicted   
    missed_moves = legal_moves_set - moves_set

    # Illegal Moves Predicted: moves that are predicted but not legal
    illegal_moves = moves_set - legal_moves_set

    # Return the results
    return list(correct_moves), list(missed_moves), list(illegal_moves)