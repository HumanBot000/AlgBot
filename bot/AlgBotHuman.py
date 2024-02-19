import json
import os
import random
import time
import MoveGenerator as mg
import chess
import chess.svg

game = chess.Board()
SHOW_SVG = True
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



def show_board_svg():
    boardsvg = chess.svg.board(game, size=600, coordinates=True)
    with open('temp.svg', 'w') as outputfile:
        outputfile.write(boardsvg)
    time.sleep(0.1)
    if SHOW_SVG: os.startfile('temp.svg')


def handle_bot(my_color):
    move = mg.generate_move(game.fen(), my_color)
    game.push(move)
    print(f">ToBot: {move}")

while not game.is_game_over():
    show_board_svg()
    print(game)
    if BOT_PLAYS_AS == chess.BLACK:
        handle_user()
        if game.is_game_over():
            break
        show_board_svg()
        handle_bot(BOT_PLAYS_AS)
    else:
        handle_bot(BOT_PLAYS_AS)
        show_board_svg()
        if game.is_game_over():
            break
        handle_user()
