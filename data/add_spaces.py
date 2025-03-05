import pandas as pd

def add_spaces_fen(fen: str) -> str:
    """Adds spaces between each character,
    preserving slashes and spaces."""
    return " ".join(fen.replace(" ", "  "))  # Preserve spaces with extra spacing

# Load the CSV file
csv_filepath = "chess_challenges_train_10k.csv"
df = pd.read_csv(csv_filepath)

# Add the FEN_space column
df["FEN_space"] = df["FEN"].apply(add_spaces_fen)

# Save the modified DataFrame back to CSV (overwrite or create a new file)
df.to_csv("chess_challenges_train_10k_spaces.csv", index=False)
