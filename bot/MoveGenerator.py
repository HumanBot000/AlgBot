import json
import os
import random
import time
from pathlib import Path

import chess
import chess.svg


INFINITY = 10000000
def get_difference(game,color):
    if color == chess.BLACK:
        return get_current_score(game,chess.BLACK) - get_current_score(game,chess.WHITE)
    return get_current_score(game,chess.WHITE) - get_current_score(game,chess.BLACK)


def position_score(score, color,game):
    with open(Path('config/filePositionAdvantages.json'), 'r') as f:
        json_file_files = json.loads(f.read())
    with open(Path('config/rankPositionAdvantages.json'), 'r') as f:
        json_file_ranks = json.loads(f.read())
    for square in game.pieces(chess.KNIGHT, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_file_files["KnightWhite"][str(number)])
        else:
            score += int(json_file_files["KnightBlack"][str(number)])
        score += int(json_file_ranks["Knight"][str(letter)])
    for square in game.pieces(chess.PAWN, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_file_files["PawnWhite"][str(number)])
        else:
            score += int(json_file_files["PawnBlack"][str(number)])
    for square in game.pieces(chess.BISHOP, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_file_files["BishopWhite"][str(number)])
        else:
            score += int(json_file_files["BishopBlack"][str(number)])
        score += int(json_file_ranks["Bishop"][str(letter)])
    return score


def check_passing_pawn(game,score,color=chess.BLACK):
    if len(game.pieces(chess.PAWN, color)) == 0:
        return score
    for my_piece_position in game.pieces(chess.PAWN, color):
        file = chess.square_file(my_piece_position)
        rank = chess.square_rank(my_piece_position)
        if not file == 0 or file == 7:
            files = [file-1,file,file+1]
        elif file == 0:
            files = [file,file+1]
        elif file == 7:
            files = [file-1,file]
        for scanning_file in files:
            if color == chess.WHITE:
                for scanning_rank in range(rank,8):
                    if game.piece_at(chess.square(scanning_file,scanning_rank)) is not None and game.piece_at(chess.square(scanning_file,scanning_rank)).piece_type == chess.PAWN and game.piece_at(chess.square(scanning_file,scanning_rank)).color == get_opposite_color(color):
                        return score
            else:
                for scanning_rank in range(rank,0,-1):
                    if game.piece_at(chess.square(scanning_file,scanning_rank)) is not None and game.piece_at(chess.square(scanning_file,scanning_rank)).piece_type == chess.PAWN and game.piece_at(chess.square(scanning_file,scanning_rank)).color == get_opposite_color(color):
                        return score
    print("PASSING PAWN")
    return score+2.4

def get_opposite_color(color):
    if color == chess.WHITE:
        return chess.BLACK
    else:
        return chess.WHITE

def get_current_score(game,color=chess.BLACK):
    score = 0
    score += len(game.pieces(chess.PAWN, color)) * 1
    score += len(game.pieces(chess.BISHOP, color)) * 3
    score += len(game.pieces(chess.KNIGHT, color)) * 3
    score += len(game.pieces(chess.ROOK, color)) * 5
    score += len(game.pieces(chess.QUEEN, color)) * 9
    if game.outcome() != None and game.outcome().winner == color:
        score += INFINITY
    elif game.outcome() != None and game.outcome().winner == get_opposite_color(color):
        score -= INFINITY
    score = position_score(score, color,game)
    score = check_passing_pawn(game,score,color)
    return score


def show_board_svg(game,SHOW_SVG = False):
    boardsvg = chess.svg.board(game, size=600, coordinates=True)
    with open('temp.svg', 'w') as outputfile:
        outputfile.write(boardsvg)
    time.sleep(0.1)
    if SHOW_SVG: os.startfile('temp.svg')


def handle_bot(my_color,game):
    if my_color == chess.WHITE:
        opponent_color = chess.BLACK
    else:
        opponent_color = chess.WHITE
    my_best_move_rating = -INFINITY
    my_best_moves = []
    for my_move in game.legal_moves:
        game.push(my_move)
        opponent_best_move_rating = -INFINITY
        opponent_best_move = None
        for opponent_move in game.legal_moves:
            game.push(opponent_move)
            if get_difference(game,opponent_color) > opponent_best_move_rating:
                opponent_best_move_rating = get_difference(game,opponent_color)
                opponent_best_move = opponent_move
            game.pop()
        game.push(opponent_best_move)
        if get_difference(game,my_color) > my_best_move_rating:
            my_best_move_rating = get_difference(game,my_color)
            my_best_moves = [my_move]
        elif get_difference(game,my_color) == my_best_move_rating:
            my_best_moves.append(my_move)
        game.pop()
        game.pop()
    my_best_move = random.choice(my_best_moves)
    game.push(my_best_move)
    return my_best_move
def generate_move(fen,color):
    game = chess.Board(fen)
    return handle_bot(color,game)