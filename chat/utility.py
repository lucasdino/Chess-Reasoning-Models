import re
import random
import typing
from typing import List
from collections import defaultdict


# ====================================================
# Defining a couple custom exceptions
# ====================================================
class TimeoutError(Exception):
    """Exception raised when the chat request times out."""

    def __init__(self, message="The request timed out."):
        super().__init__(message)


class GenerationError(Exception):
    """Exception raised when the generation fails."""

    def __init__(self, message="The generation failed."):
        super().__init__(message)


class ExtractionError(Exception):
    """Exception raised when we're unable to properly extract the answer from the model."""

    def __init__(
        self,
        message="Model generation not formatted properly -- unable to extract answer.",
    ):
        super().__init__(message)


class IllegalMoveError(Exception):
    """Exception raised when the model generates an illegal move."""

    def __init__(self, message="The model generated an illegal move."):
        super().__init__(message)


# ====================================================
# Defining a couple custom exceptions
# ====================================================
def extract_answer(text: str) -> str:
    """
    Extracts text between <answer> and </answer> tags, trims it, and returns it.
    Raises ExtractionError if no such text exists.

    Args:
        text (str): The input string containing the <answer> tags.

    Returns:
        str: The trimmed extracted text.

    Raises:
        ExtractionError: If the <answer> tags are not found.
    """
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if not match:
        raise ExtractionError("No <answer> tags found.")

    # Strip leading/trailing whitespace and quotes
    extracted = match.group(1).strip()
    extracted = re.sub(
        r'^["\']|["\']$', "", extracted
    )  # Remove single/double quotes at edges

    # Ensure it only contains alphanumeric characters
    if not re.fullmatch(r"[A-Za-z0-9 ]+", extracted):
        raise ExtractionError("Extracted text contains invalid characters.")

    return extracted


def fen_to_description(fen: str) -> str:
    """
    Converts a FEN (Forsyth-Edwards Notation) string into a human-readable chessboard description.

    Args:
        fen (str): The FEN string representing the board state.

    Returns:
        str: A formatted description of the board state.
    """
    piece_map = {
        "K": "King",
        "Q": "Queen",
        "R": "Rook",
        "B": "Bishop",
        "N": "Knight",
        "P": "Pawn",
        "k": "King",
        "q": "Queen",
        "r": "Rook",
        "b": "Bishop",
        "n": "Knight",
        "p": "Pawn",
    }

    try:
        fen_parts = fen.split()
        if len(fen_parts) < 2:
            raise ValueError(
                "Invalid FEN format. Ensure it has at least a board position and turn information."
            )

        ranks = fen_parts[0].split("/")
        if len(ranks) != 8:
            raise ValueError("Invalid FEN format. The board should have 8 ranks.")

        turn = "White to move." if fen_parts[1] == "w" else "Black to move."
        board = []

        for r, rank in enumerate(ranks):
            row = []
            file = 0
            for char in rank:
                if char.isdigit():
                    file += int(char)
                elif char in piece_map:
                    row.append((char, file, 8 - r))  # (Piece, File, Rank)
                    file += 1
                else:
                    raise ValueError(f"Invalid character '{char}' in FEN notation.")
            board.extend(row)

        piece_positions = defaultdict(list)

        for piece, file, rank in board:
            color = "White" if piece.isupper() else "Black"
            piece_type = piece_map[piece]
            position = f"{chr(file + 97)}{rank}"
            piece_positions[(color, piece_type)].append(position)

        description = [turn]

        for (color, piece_type), positions in sorted(
            piece_positions.items(), key=lambda x: (x[0][0], x[0][1])
        ):
            position_text = ", ".join(positions)
            description.append(
                f"{color} {piece_type}{'s' if len(positions) > 1 else ''} on {position_text}."
            )

        return "\n".join(description)

    except ValueError as e:
        return f"Error processing FEN: {e}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def format_prompt(board: str, legal_moves: List[str]) -> str:
    """
    Formats the board and legal moves into a prompt for the model.

    Args:
        board (str): The current board state.
        legal_moves (List[str]): The list of legal moves.

    Returns:
        str: The formatted prompt.
    """
    random.shuffle(legal_moves)
    prompt = f"<FEN> {board} </FEN> <legalmoves> {legal_moves} </legalmoves>"
    prompt = prompt.replace("'", "")
    return prompt
