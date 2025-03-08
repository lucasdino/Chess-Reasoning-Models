from engine.stockfish import Engine, StockfishEngine
import chess
import chess.pgn
import datetime

# We use a stockfish engine to evaluate the current board and terminate the
# game early if the score is high enough (i.e., _MIN_SCORE_TO_STOP).
_EVAL_STOCKFISH_ENGINE = StockfishEngine(
    name="eval",
    limit=chess.engine.Limit(time=0.01)
)
_MIN_SCORE_TO_STOP = 1300

def _play_game(
    engines: tuple[Engine, Engine],
    engines_names: tuple[str, str],
    white_name: str,
    initial_board: chess.Board | None = None,
) -> chess.pgn.Game:
  """Plays a game of chess between two engines.

  Args:
    engines: The engines to play the game.
    engines_names: The names of the engines.
    white_name: The name of the engine playing white.
    initial_board: The initial board (if None, the standard starting position).

  Returns:
    The game played between the engines.
  """
  if initial_board is None:
    initial_board = chess.Board()
  white_player = engines_names.index(white_name)
  current_player = white_player if initial_board.turn else 1 - white_player
  board = initial_board
  result = None
  print(f'Starting FEN: {board.fen()}')

  while not (
      board.is_game_over()
      or board.can_claim_fifty_moves()
      or board.is_repetition()
  ):
    best_move = engines[current_player].play(board)
    # print(f'Best move: {best_move.uci()}')

    # Push move to the game.
    board.push(best_move)
    current_player = 1 - current_player

    # We analyse the board once the last move is done and pushed.
    info = _EVAL_STOCKFISH_ENGINE.analyse(board)
    score = info['score'].relative
    if score.is_mate():
      is_winning = score.mate() > 0
    else:
      is_winning = score.score() > 0
    score_too_high = score.is_mate() or abs(score.score()) > _MIN_SCORE_TO_STOP

    if score_too_high:
      is_white = board.turn == chess.WHITE
      if is_white and is_winning or (not is_white and not is_winning):
        result = '1-0'
      else:
        result = '0-1'
      break
  print(f'End FEN: {board.fen()}')

  game = chess.pgn.Game.from_board(board)
  game.headers['Event'] = 'ELO Eval'
  game.headers['Date'] = datetime.datetime.today().strftime('%Y.%m.%d')
  game.headers['White'] = white_name
  game.headers['Black'] = engines_names[1 - white_player]
  if result is not None:  # Due to early stopping.
    game.headers['Result'] = result
  else:
    game.headers['Result'] = board.result(claim_draw=True)
  return game


if __name__ == "__main__":
    # Initialize Stockfish engines for both players
    engine_white = StockfishEngine(limit=chess.engine.Limit(time=0.01))
    engine_black = StockfishEngine(limit=chess.engine.Limit(time=0.01))
    engine_white.elo = 2800
    engine_black.elo = 1500


    engines = (engine_white, engine_black)
    engines_names = ("Stockfish_White", "Stockfish_Black")
    white_name = "Stockfish_White"

    game = _play_game(engines, engines_names, white_name)

    # Print the game in PGN format
    print(game)

    #close engines to end the program
    engine_white.close()
    engine_black.close()
    _EVAL_STOCKFISH_ENGINE.close()