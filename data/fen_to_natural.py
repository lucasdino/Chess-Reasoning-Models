import re
import csv
import ast

def fen_to_natural(fen: str) -> str:
    piece_map = {
        'K': 'White King', 'Q': 'White Queen', 'R': 'White Rook', 'B': 'White Bishop', 'N': 'White Knight', 'P': 'White Pawn',
        'k': 'Black King', 'q': 'Black Queen', 'r': 'Black Rook', 'b': 'Black Bishop', 'n': 'Black Knight', 'p': 'Black Pawn'
    }
    
    parts = fen.split()
    board_fen, turn, castling, en_passant, halfmove, fullmove = parts[:6]
    
    board_rows = board_fen.split('/')
    board = []
    
    for r, row in enumerate(board_rows):
        expanded_row = ''
        for char in row:
            if char.isdigit():
                expanded_row += '.' * int(char)
            else:
                expanded_row += char
        board.append(expanded_row)
    
    natural_description = []
    natural_description.append(f"{'White' if turn == 'w' else 'Black'} to move.")
    
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != '.':
                natural_description.append(f"{piece_map[piece]} on {chr(97 + c)}{8 - r}.")
    
    if castling != '-':
        castling_rights = ' '.join([f"{('White' if c.isupper() else 'Black')} {'King-side' if c in 'Kk' else 'Queen-side'} castling" for c in castling])
        natural_description.append(f"Castling rights: {castling_rights}.")
    
    if en_passant != '-':
        natural_description.append(f"En Passant available on {en_passant}.")
    
    natural_description.append(f"Move number: {fullmove}.")
    
    return ' '.join(natural_description)

def parse_csv():
    parsed = []
    filename = "chess_challenges_full.csv"
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row_num, row in enumerate(reader, 1):
            # Skip empty rows
            if not row:
                continue
                
            fen = row[0].strip()
            moves_str = row[1].strip()
            probs_str = row[2].strip()
            if fen == "FEN":
                continue
            # Convert string representations to actual lists
            legal_moves = ast.literal_eval(moves_str)
            probabilities = [float(p) for p in ast.literal_eval(probs_str)]
            
            parsed.append((fen, legal_moves, probabilities))
    return parsed

def write_translation(outname):
    parsed_lines = parse_csv()
    with open(outname, 'w') as outfile:
        for fen, moves, probs in parsed_lines:
            moves_and_probs= zip(moves, probs)
            translation = fen_to_natural(fen)
            outfile.write(translation + "\n")
            outfile.write("Legal moves and probabilities:\n")
            for move, prob in moves_and_probs:
                outfile.write(f"Move: {move}, Probability: {prob}\n")
            outfile.write("\n")
            



if __name__ == "__main__":
    write_translation("natural_language_samples.txt")



