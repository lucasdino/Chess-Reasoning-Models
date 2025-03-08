import random

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