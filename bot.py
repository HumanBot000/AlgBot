import json
import os
import random
import time

import chess
import chess.svg

game = chess.Board()
INFINITY = 100000
SHOW_SVG = True


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


def get_difference(color=chess.BLACK):
    if color == chess.BLACK:
        return get_current_score(chess.BLACK) - get_current_score(chess.WHITE)
    return get_current_score(chess.WHITE) - get_current_score(chess.BLACK)


def position_score(score, color):
    with open('filePositionAdvantages.json', 'r') as f:
        json_file = json.loads(f.read())
    for square in game.pieces(chess.KNIGHT, color):
        number = chess.square_file(square)
        letter = chess.square_rank(square)+1
        if color == chess.WHITE:
            score += int(json_file["KnightWhite"][str(number)])
        else:
            score += int(json_file["KnightBlack"][str(number)])

def get_current_score(color=chess.BLACK):
    score = 0
    score += len(game.pieces(chess.PAWN, color)) * 1
    score += len(game.pieces(chess.BISHOP, color)) * 3
    score += len(game.pieces(chess.KNIGHT, color)) * 3
    score += len(game.pieces(chess.ROOK, color)) * 5
    score += len(game.pieces(chess.QUEEN, color)) * 9
    if game.outcome() != None and game.outcome().winner == color:
        score += INFINITY
    elif game.outcome() != None and game.outcome().winner != color:
        score -= INFINITY
    position_score(score, color)
    return score


def show_board_svg():
    boardsvg = chess.svg.board(game, size=600, coordinates=True)
    with open('temp.svg', 'w') as outputfile:
        outputfile.write(boardsvg)
    time.sleep(0.1)
    if SHOW_SVG: os.startfile('temp.svg')


def handle_bot():
    my_best_move_rating = -1000
    my_best_move = None
    for my_move in game.legal_moves:
        game.push(my_move)
        opponent_best_move_rating = -1000
        opponent_best_move = None
        for opponent_move in game.legal_moves:
            game.push(opponent_move)
            if get_difference(chess.WHITE) > opponent_best_move_rating:
                opponent_best_move_rating = get_difference(chess.WHITE)
                opponent_best_move = opponent_move
            game.pop()
        game.push(opponent_best_move)
        if get_difference(chess.BLACK) > my_best_move_rating:
            my_best_move_rating = get_difference(chess.BLACK)
            my_best_move = my_move
        game.pop()
        game.pop()
    game.push(my_best_move)
    print(f">Bot: {my_best_move}")
    return my_best_move


while not game.is_game_over():
    show_board_svg()
    print(game)
    handle_user()
    if game.is_game_over():
        break
    show_board_svg()
    handle_bot()
