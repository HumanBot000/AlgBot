import os
import chess.pgn
import chess
from stockfish import Stockfish

import MoveGenerator as mg

game = chess.Board()
current_directory = os.path.dirname(__file__)
engines_directory = os.path.join(current_directory, '..', 'engines')
stockfish_path = os.path.join(engines_directory, 'stockfish/stockfish-windows-x86-64-avx2.exe')
stockfish = Stockfish(path=stockfish_path)
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
    move = mg.generate_move(game.fen(), chess.WHITE)
    game.push(move)
    node = node.add_variation(move)
    """move = mg.generate_move(game.fen(), chess.WHITE)
    game.push(move)
    print(f">ToBot: {move}")
    print(game)
    stockfish.set_fen_position(game.fen())
    move = stockfish.get_best_move()
    game.push(chess.Move.from_uci(move))
    print(f"Stockfish: {move}")
    print(game)
    print(stockfish.get_wdl_stats())"""
print(game.outcome().result())
print(game_pgn)