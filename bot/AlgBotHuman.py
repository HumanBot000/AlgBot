import os
import time
import MoveGenerator as mg
import chess

game = chess.Board()
BOT_PLAYS_AS = chess.BLACK
def handle_user():
    user_move = input(">You:")
    try:
        game.push_san(user_move)
    except chess.IllegalMoveError:
        print("Illegal Move!")
        handle_user()
    except chess.InvalidMoveError:
        print("Invalid Move!")
        handle_user()
    except chess.AmbiguousMoveError:
        print("Ambiguous Move!")
        handle_user()
    except Exception as e:
        print(e)
        handle_user()




while not game.is_game_over():
    mg.show_board_svg(game)
    print(game)
    if BOT_PLAYS_AS == chess.BLACK:
        handle_user()
        if game.is_game_over():
            break
        game.push(mg.generate_move(game.fen(), BOT_PLAYS_AS))
    else:
        game.push(mg.generate_move(game.fen(), BOT_PLAYS_AS))
        mg.show_board_svg(game)
        if game.is_game_over():
            break
        handle_user()
