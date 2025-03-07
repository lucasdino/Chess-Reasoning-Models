import ast
import pandas as pd
import chess

def convert_uci_moves_to_pgn(fen, uci_moves):
    """
    Convert UCI moves to PGN move notation based on a given FEN position.
    """
    board = chess.Board(fen)
    pgn_moves = []
    
    for uci in uci_moves:
        move = chess.Move.from_uci(uci)
        if move in board.legal_moves:
            pgn_moves.append(board.san(move)) 

    return pgn_moves

def load_challenge_moves_csv(filepath: str, move_notation: str = 'UCI', shuffle: bool = True) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame, converts list-like string columns into actual lists,
    removes single apostrophes from 'Move' column values, and optionally shuffles the DataFrame.
    
    Also converts UCI moves to PGN if 'move_notation' is 'UCI'.

    Args:
        filepath (str): Path to the CSV file.
        move_notation (str): Type of notation to process ('UCI' or 'PGN').
        shuffle (bool): Whether to shuffle the DataFrame (default is True).

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    df = pd.read_csv(filepath)

    # Convert the columns from strings to lists (using ast.literal_eval)
    df["Move"] = df["Move"].apply(lambda x: [move.replace("'", "") for move in ast.literal_eval(x)])
    df["Win Probability"] = df["Win Probability"].apply(ast.literal_eval)

    if move_notation == 'PGN':
        # Apply conversion
        df["Move"] = df.apply(lambda row: convert_uci_moves_to_pgn(row["FEN"], row["Move"]), axis=1)

    if shuffle:
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df
