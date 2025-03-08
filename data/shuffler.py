import pandas as pd
import random

# Load dataset from CSV
df = pd.read_csv("chess_challenges_full.csv")

# Function to shuffle moves and probabilities together for each row
def shuffle_moves(entry):
    try:
        # Convert string representations of lists into actual lists
        moves = eval(entry["Move"]) if isinstance(entry["Move"], str) else entry["Move"]
        win_probs = eval(entry["Win Probability"]) if isinstance(entry["Win Probability"], str) else entry["Win Probability"]

        # Zip moves and probabilities together, shuffle, and unzip
        combined = list(zip(moves, win_probs))
        random.shuffle(combined)
        shuffled_moves, shuffled_probs = zip(*combined)

        return pd.Series([list(shuffled_moves), list(shuffled_probs)])
    except Exception as e:
        print(f"Error processing row: {entry}")
        print(f"Exception: {e}")
        return pd.Series([entry["Move"], entry["Win Probability"]])  # Return unchanged on error

# Apply shuffling to each row
df[["Move", "Win Probability"]] = df.apply(shuffle_moves, axis=1)

# Save shuffled dataset to a new CSV
df.to_csv("chess_challenges_full_shuffled.csv", index=False)

# Display confirmation
print("Shuffled dataset saved!")
