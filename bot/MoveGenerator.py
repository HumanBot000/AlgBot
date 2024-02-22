import json
import os
import random
import time
from pathlib import Path
import chess.polyglot
import chess
import chess.svg

INFINITY = 1000000000
USE_OPENING_BIN = False
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 330,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}
TAKE_DRAW_WHEN_LOOSING_THRESHOLD = 3


def get_difference(game, color):
    if color == chess.BLACK:
        return get_current_score(game=game, color=chess.BLACK) - get_current_score(game=game, color=chess.WHITE)
    return get_current_score(game=game, color=chess.WHITE) - get_current_score(game=game, color=chess.BLACK)

def piece_table_score(score,color,game):
    if color == chess.WHITE:
        with open(Path('config/Piece-Square Tables/white.json'), 'r') as f:
            table = json.loads(f.read())
    else:
        with open(Path('config/Piece-Square Tables/black.json'), 'r') as f:
            table = json.loads(f.read())
    for Pawn in game.pieces(chess.PAWN,color):
        score += (int(table["Pawn"][chess.square_rank(Pawn)][chess.square_file(Pawn)]))
    for Knight in game.pieces(chess.KNIGHT,color):
        score += (int(table["Knight"][chess.square_rank(Knight)][chess.square_file(Knight)]))
    for Bishop in game.pieces(chess.BISHOP,color):
        score += (int(table["Bishop"][chess.square_rank(Bishop)][chess.square_file(Bishop)]))
    for Rook in game.pieces(chess.ROOK,color):
        score += (int(table["Rook"][chess.square_rank(Rook)][chess.square_file(Rook)]))
    for Queen in game.pieces(chess.QUEEN,color):
        score += (int(table["Queen"][chess.square_rank(Queen)][chess.square_file(Queen)]))
    for King in game.pieces(chess.KING,color):
        score += (int(table["King"][chess.square_rank(King)][chess.square_file(King)]))
    return score
def position_score(score, color, game):
    return piece_table_score(score,color,game)
    """This Function is deprecated and uses official tables now"""
    with open(Path('config/filePositionAdvantages.json'), 'r') as f:
        json_files = json.loads(f.read())
    with open(Path('config/rankPositionAdvantages.json'), 'r') as f:
        json_ranks = json.loads(f.read())
    for square in game.pieces(chess.KNIGHT, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_files["KnightWhite"][str(letter)])
        else:
            score += int(json_files["KnightBlack"][str(letter)])
        score += int(json_ranks["Knight"][str(number)])
    for square in game.pieces(chess.PAWN, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_ranks["PawnWhite"][str(number)])
        else:
            score += int(json_ranks["PawnBlack"][str(number)])
    for square in game.pieces(chess.BISHOP, color):
        number = chess.square_rank(square) + 1
        letter = chess.square_file(square) + 1
        if color == chess.WHITE:
            score += int(json_files["BishopWhite"][str(letter)])
        else:
            score += int(json_files["BishopBlack"][str(letter)])
        score += int(json_ranks["Bishop"][str(number)])
    return score


def check_passing_pawn(game, score,my_piece_position,color=chess.BLACK):#todo double pawn check
    if len(game.pieces(chess.PAWN, color)) == 0:
        return score
    file = chess.square_file(my_piece_position)
    rank = chess.square_rank(my_piece_position)
    if file not in [0, 7]:
        files = [file - 1, file, file + 1]
    elif file == 0:
        files = [file, file + 1]
    elif file == 7:
        files = [file - 1, file]
    for scanning_file in files:
        for scanning_rank in range(rank+1, 8) if color == chess.WHITE else range(rank-1, 0, -1):
            if game.piece_at(chess.square(scanning_file, scanning_rank)) is not None and game.piece_at(chess.square(scanning_file, scanning_rank)).piece_type == chess.PAWN and game.piece_at(chess.square(scanning_file, scanning_rank)).color == get_opposite_color(color):
                return score
    print("Passing Pawn",game.fen(),chess.square_file(my_piece_position),chess.square_rank(my_piece_position))
    return score + 0


def get_opposite_color(color):
    if color == chess.WHITE:
        return chess.BLACK
    else:
        return chess.WHITE


def get_current_score(game, color:chess.Color=chess.BLACK,x=False):
    score = 0
    score += len(game.pieces(chess.PAWN, color)) * 100
    score += len(game.pieces(chess.BISHOP, color)) * 330
    score += len(game.pieces(chess.KNIGHT, color)) * 320
    score += len(game.pieces(chess.ROOK, color)) * 500
    score += len(game.pieces(chess.QUEEN, color)) * 900
    score = piece_table_score(score=score, color=color, game=game)
    for my_piece_position in game.pieces(chess.PAWN, color):
        score = check_passing_pawn(game, score, my_piece_position, color)
    if game.outcome() is not None and game.outcome().winner == color:
        score += INFINITY
    elif game.outcome() is not None and game.outcome().winner == get_opposite_color(color):
        score -= INFINITY
    elif game.outcome() is not None and x == True and game.outcome().result() == "1/2-1/2" and score + TAKE_DRAW_WHEN_LOOSING_THRESHOLD < get_current_score(game=game,
                                                                                                        color=get_opposite_color(
                                                                                                                color),x=True):  # Check if it makes sense to draw
        score += INFINITY
    return score


def show_board_svg(game, SHOW_SVG=True):
    boardsvg = chess.svg.board(game, size=600, coordinates=True)
    with open('temp.svg', 'w') as outputfile:
        outputfile.write(boardsvg)
    time.sleep(0.1)
    if SHOW_SVG: os.startfile('temp.svg')


def handle_bot(my_color, game):
    """
    File = A, B, C, D, E, F, G, H
    Rank = 1, 2, 3, 4, 5, 6, 7, 8
            Mein Gedächtnisdialog:
            0. Das Ausgagngsboard wird ab jetzt als B0 bezeichnet
            1. Mein bester Move wird auf den erst möglichen gesetzt. Falls alle schlechter sind als dieser, wird dieser am Ende gespielt.
            1.5 Es wird durch jeden möglichen move geloopt (M1)
            2. Der Move wird ausgeführt (M1)
            3. Das beste rating des gegners wird auf -INF  gesetzt.
            4. Es wird der erste Move des Gegners als bester Move gesetzt. Falls alle schlechter sind als dieser, wird dieser am Ende gespielt.
            5. Es wird durch jeden möglichen Move des gegners geloopt.(M2)
            6. Der Move wird ausgeführt (M2)
            6.5 Es wird eine Bewertung des Spielfeldes berechnet. Diese besteht aus dem Score des Gegners - dem Score des Bots.
            7. Wenn die aktuelle Bewertung des gegners besser ist, als die Bewertung bei seinem jetzigen besten Spielzug, wird dieser als neuer  bestOpponentMove gesetzt.
            8. Der letzte zug des gegners wird zurück genommen. (M2)
            9. Für die weitere Berechnung des besten Zuges des Bots, wird nun angenommen das der Gegner bestOpponentMove spielt. Deshalb wird das auf dem aktuellen Spielfeld gespeichert.
            |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
            |10. Jetzt wird berechnet, wie gut der Aktuelle Zug (M1) ist, wenn einberechnet wird, dass der Gegner bestOpponentMove spielt. Dafür wird wieder der selbe Score berechnet. (Nur halt umgedreht).|
            |    Wenn der Zug M1 jetzt eine bessere bewertung hat als der jetzige beste Move des Bots, wird dieser als neuer bester Zug markiert.                                                            |
            |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|  
            12. Sowohl der bestOpponentMove als auch M1 werden zurück gesetzt, damit B0 für den nächsten Loopvorgang wieder vorhanden ist.
            13. Der beste Move des Bots wird returnt.
    """
    if USE_OPENING_BIN:
        with chess.polyglot.open_reader("openings/Ranomi 1.4.bin") as reader:
            for entry in reader.find_all(game):
                return entry.move
    my_best_move_rating = -INFINITY
    for move_temp in game.legal_moves:
        first_possible_move = move_temp
        break
    my_best_moves = [first_possible_move]
    del first_possible_move
    for my_move in game.legal_moves:
        game.push(my_move)
        opponent_best_move_rating = -INFINITY
        first_possible_move = None
        for move_temp in game.legal_moves:
            first_possible_move = move_temp
            break
        opponent_best_move = first_possible_move
        if first_possible_move is None:  # My Move leads to checkmate
            return my_move
        for opponent_move in game.legal_moves:
            game.push(opponent_move)
            if get_difference(game=game, color=get_opposite_color(my_color)) > opponent_best_move_rating:
                opponent_best_move_rating = get_difference(game, get_opposite_color(my_color))
                opponent_best_move = opponent_move
                #print(f"best response to {my_move} is {opponent_best_move} with {opponent_best_move_rating}")
            game.pop()
        game.push(opponent_best_move)
        if get_difference(game, my_color) > my_best_move_rating:
            my_best_move_rating = get_difference(game, my_color)
            my_best_moves = [my_move]
        elif get_difference(game, my_color) == my_best_move_rating:
            my_best_moves.append(my_move)
        #print(my_move, get_difference(game, my_color), my_best_moves, opponent_best_move)
        game.pop()
        game.pop()
    my_best_move = random.choice(my_best_moves)
    print(my_best_move)
    return my_best_move


def generate_move(fen, color):
    game = chess.Board(fen)
    return handle_bot(my_color=color, game=game)
