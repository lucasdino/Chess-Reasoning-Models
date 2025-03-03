import ast
import pandas as pd


def load_challenge_moves_csv(filepath: str, shuffle: bool = True) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame, converts list-like string columns into actual lists,
    removes single apostrophes from 'Move' column values, and optionally shuffles the DataFrame.

    Args:
        filepath (str): Path to the CSV file.
        shuffle (bool): Whether to shuffle the DataFrame (default is True).

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    df = pd.read_csv(filepath)

    # Convert the columns from strings to lists (using ast.literal_eval)    
    df["Move"] = df["Move"].apply(lambda x: [move.replace("'", "") for move in ast.literal_eval(x)])
    df["Win Probability"] = df["Win Probability"].apply(ast.literal_eval)

    if shuffle:
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df