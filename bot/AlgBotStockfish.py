import os
import chess.pgn
import chess
from stockfish import Stockfish

import MoveGenerator as mg

current_directory = os.path.dirname(__file__)
engines_directory = os.path.join(current_directory, '..', 'engines')
stockfish_path = os.path.join(engines_directory, 'stockfish/stockfish-windows-x86-64-avx2.exe')
stockfish = Stockfish(path=stockfish_path)

elo = 100

while True:
    stockfish.set_elo_rating(elo)
    game = chess.Board()
    game_pgn = chess.pgn.Game()
    game_pgn.headers["Event"] = "ToBot VS. Stockfish"

    move = mg.generate_move(game.fen(), chess.WHITE)

    node = game_pgn.add_variation(move)
    game.push(move)
    while not game.is_game_over():
        stockfish.set_fen_position(game.fen())
        move = stockfish.get_best_move()
        game.push(chess.Move.from_uci(move))
        node = node.add_variation(chess.Move.from_uci(move))
        if game.is_game_over():
            break
        # Bot's turn
        move = mg.generate_move(game.fen(), chess.WHITE)
        game.push(move)
        node = node.add_variation(move)
    if game.outcome().winner == chess.WHITE:
        game_pgn.headers["Result"] = "ToBot"
        print(f"Won with:{elo}")
        break
    elif game.outcome().winner == None:
        game_pgn.headers["Result"] = "Draw"
        print(f"Draw with:{elo}")
    else:
        game_pgn.headers["Result"] = "Stockfish"
        print(f"Lost with:{elo}")
        elo -= 100
    print(game_pgn)
print(game_pgn)
