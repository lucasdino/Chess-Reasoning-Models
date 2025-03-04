# Python file that converts our data into a valid parquet file (train and test)
# Follows a similar structure as this: https://github.com/volcengine/verl/blob/main/examples/data_preprocess/gsm8k.py
# Which is better explain by their docs here: https://verl.readthedocs.io/en/latest/preparation/prepare_data.html

# Drop this into the 'verl/examples/data_prepocess/' folder

import os
import ast
import random
import argparse
import numpy as np
from typing import List

import pandas as pd

from verl.utils.hdfs_io import copy, makedirs


# =============================================================================
# Extraction Functionality (extracts move from final generation)
# =============================================================================
# def create_reward_dict(move: List[str], win_prob: List[float]) -> dict:
#     """
#     Takes in two lists -- a list of legal moves and a list of associated win probabilities.
#     First processes the win_prob list to produce rewards and then creates a reward dictionary that is returned.
#     """    
#     # TODO
#     return {m: k for m, k in zip(move, win_prob)}
def create_reward_dict(move: List[str], win_prob: List[float]) -> dict:
    """
    Takes in two lists -- a list of legal moves and a list of associated win probabilities.
    Zips them together into a NumPy array, normalizes the win probabilities using min-max scaling 
    so that they lie between 0 and 1, and returns a dictionary mapping each move to its normalized win probability.
    """
    # Create a numpy array from the zipped moves and win probabilities.
    arr = np.array(list(zip(move, win_prob)), dtype=object)
    
    # Extract the win probability values and convert to float.
    win_probs = np.array(arr[:, 1], dtype=float)
    
    # Apply min-max normalization.
    min_val = win_probs.min()
    max_val = win_probs.max()
    if max_val - min_val > 0:
        normalized_win_probs = (win_probs - min_val) / (max_val - min_val)
    else:
        # If all values are the same, set them to 0.5.
        normalized_win_probs = np.full_like(win_probs, 0.5)
    
    # Create a dictionary mapping each move to its normalized win probability.
    reward_dict = {m: float(p) for m, p in zip(arr[:, 0], normalized_win_probs)}
    return reward_dict


# =============================================================================
# Data Processing Helper Functions
# =============================================================================
def _load_challenge_moves_csv(filepath: str, shuffle: bool = True, max_samples: int = None) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame, converts list-like string columns into actual lists,
    removes single apostrophes from 'Move' column values, and optionally shuffles the DataFrame.
    Allows limiting the number of rows returned.

    Args:
        filepath (str): Path to the CSV file.
        shuffle (bool): Whether to shuffle the DataFrame (default is True).
        max_samples (int, optional): Maximum number of rows to return. If None, returns all rows.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    df = pd.read_csv(filepath)

    # Convert the columns from strings to lists (using ast.literal_eval)    
    df["Move"] = df["Move"].apply(lambda x: [move.replace("'", "") for move in ast.literal_eval(x)])
    df["Win Probability"] = df["Win Probability"].apply(ast.literal_eval)

    # Optional processing (based on args)
    if shuffle:
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    if max_samples is not None:
        df = df.head(max_samples)

    return df



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



# =============================================================================
# Functionality for veRL Data Preprocessing
# =============================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='~/chess_data')
    parser.add_argument('--hdfs_dir', default=None)

    args = parser.parse_args()

    train_dataset = _load_challenge_moves_csv(
        filepath='chess_data/chess_challenges_train_10k.csv',
        shuffle=True,
        max_samples=None
    )
    test_dataset = _load_challenge_moves_csv(
        filepath='chess_data/chess_challenges_test_2k.csv',
        shuffle=True,
        max_samples=None
    )

    # Define the processing function
    def process_fn(example, idx, split):
        """
        Processes a single row in the dataset.

        Args:
            example (pd.Series): A row from the DataFrame.
            idx (int): The index of the row.
            split (str): The dataset split ('train' or 'test').

        Returns:
            dict: Processed row in the desired format.
        """
        question = format_prompt(board=example['FEN'], legal_moves=example['Move'])
        solution = create_reward_dict(move=example['Move'], win_prob=example['Win Probability'])

        return {
            "data_source": "chess_reasoning",
            "prompt": [{
                "role": "user",
                "content": question,
            }],
            "ability": "math",
            "reward_model": {
                "style": "rule",
                "ground_truth": solution
            },
            "extra_info": {
                'split': split,
                'index': idx
            }
        }

    # Apply transformation to train and test datasets
    train_dataset = train_dataset.apply(lambda row: process_fn(row, row.name, "train"), axis=1)
    test_dataset = test_dataset.apply(lambda row: process_fn(row, row.name, "test"), axis=1)

    # Convert back to DataFrame
    train_dataset = pd.DataFrame(train_dataset.tolist())
    test_dataset = pd.DataFrame(test_dataset.tolist())

    # Save as Parquet files
    local_dir = args.local_dir
    os.makedirs(local_dir, exist_ok=True)

    train_dataset.to_parquet(os.path.join(local_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test.parquet'))

    # Optionally copy to HDFS directory
    if hdfs_dir is not None:
        makedirs(hdfs_dir)

        copy(src=local_dir, dst=hdfs_dir)