def get_random_piece_and_position(board: str):
    """
    Selects a random piece from the given FEN board representation and returns its piece letter and position.

    Args:
        board (str): A string representing the chessboard in Forsyth-Edwards Notation (FEN).

    Returns:
        tuple: (piece_letter, position) where:
            - piece_letter (str): The letter representing the selected chess piece (e.g., 'N' for knight, 'p' for pawn).
            - position (str): The corresponding board position in algebraic notation (e.g., 'e4').
    """
    # Pseudocode:
    # 1. Define the board file (columns) as ['a' to 'h'] and ranks (rows) as ['1' to '8'].
    # 2. Parse the FEN string to extract the board layout (first segment before spaces).
    # 3. Convert the FEN board into an 8x8 matrix where empty spaces are expanded.
    # 4. Collect all non-empty squares with their piece letters and positions.
    # 5. Randomly select one from the list and return it(use maps)