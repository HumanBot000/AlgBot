import json
import os
import random
import time
from pathlib import Path
import chess.polyglot
import chess
import chess.svg

INFINITY = 10000000
USE_OPENING_BIN = False
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}
TAKE_DRAW_WHEN_LOOSING_THRESHOLD = 3


def get_difference(game, color):
    if color == chess.BLACK:
        return get_current_score(game, chess.BLACK) - get_current_score(game, chess.WHITE)
    return get_current_score(game, chess.WHITE) - get_current_score(game, chess.BLACK)

def piece_table_score(score,color,game):
    if color == chess.WHITE:
        with open(Path('config/Piece-Square Tables/white.json'), 'r') as f:
            table = json.loads(f.read())
    else:
        with open(Path('config/Piece-Square Tables/black.json'), 'r') as f:
            table = json.loads(f.read())
    for Pawn in game.pieces(chess.PAWN,color):
        score += int(table["Pawn"][chess.square_rank(Pawn)][chess.square_file(Pawn)]) / 100
    for Knight in game.pieces(chess.KNIGHT,color):
        score += int(table["Knight"][chess.square_rank(Knight)][chess.square_file(Knight)]) / 100
    for Bishop in game.pieces(chess.BISHOP,color):
        score += int(table["Bishop"][chess.square_rank(Bishop)][chess.square_file(Bishop)]) / 100
    for Rook in game.pieces(chess.ROOK,color):
        score += int(table["Rook"][chess.square_rank(Rook)][chess.square_file(Rook)]) / 100
    for Queen in game.pieces(chess.QUEEN,color):
        score += int(table["Queen"][chess.square_rank(Queen)][chess.square_file(Queen)]) / 100
    for King in game.pieces(chess.KING,color):
        score += int(table["King"][chess.square_rank(King)][chess.square_file(King)]) / 100
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
    return score + 0.5


def get_opposite_color(color):
    if color == chess.WHITE:
        return chess.BLACK
    else:
        return chess.WHITE


def get_current_score(game, color=chess.BLACK,x=False):
    score = 0
    score += len(game.pieces(chess.PAWN, color)) * 1
    score += len(game.pieces(chess.BISHOP, color)) * 3
    score += len(game.pieces(chess.KNIGHT, color)) * 3
    score += len(game.pieces(chess.ROOK, color)) * 5
    score += len(game.pieces(chess.QUEEN, color)) * 9
    score = position_score(score, color, game)
    for my_piece_position in game.pieces(chess.PAWN, color):
        score = check_passing_pawn(game, score, my_piece_position, color)
    #score = check_fork(game, score, color)
    if game.outcome() is not None and game.outcome().winner == color:
        score += INFINITY
    elif game.outcome() is not None and game.outcome().winner == get_opposite_color(color):
        score -= INFINITY
    elif game.outcome() is not None and x == True and game.outcome().result() == "1/2-1/2" and score + TAKE_DRAW_WHEN_LOOSING_THRESHOLD < get_current_score(game,
                                                                                                        get_opposite_color(
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
    for move_temp in game.legal_moves:
        first_possible_move = move_temp
        break
    with chess.polyglot.open_reader("openings/Ranomi 1.4.bin") as reader:
        for entry in reader.find_all(game):
            return entry.move
    best_moves = {"O1R": -INFINITY, "O1M": first_possible_move, "M1M": first_possible_move, "M1R": -INFINITY}#M=Move,R=Rating, M=My, O=Opponent
    for my_move in game.legal_moves:
        game.push(my_move)
        first_possible_move = None
        for move_temp in game.legal_moves:
            first_possible_move = move_temp
            break
        if first_possible_move is None:  # My Move leads to checkmate
            return my_move
        for opponent_move in game.legal_moves:
            game.push(opponent_move)
            for move_temp in game.legal_moves:
                first_possible_move = move_temp
                break
            if first_possible_move is None:  # Checkmate
                game.pop()
                best_moves["O1R"] = INFINITY
                best_moves["O1M"] = opponent_move
            else:
                if get_difference(game, get_opposite_color(my_color)) > best_moves["O1R"]:
                    best_moves["O1R"] = get_difference(game, get_opposite_color(my_color))
                    best_moves["O1M"] = opponent_move
            game.pop()
        game.push(best_moves["O1M"])
        if get_difference(game, my_color) > best_moves["M1R"]:
            best_moves["M1R"] = get_difference(game, my_color)
            best_moves["M1M"] = my_move
        game.pop()
        game.pop()
    return best_moves["M1M"]


def generate_move(fen, color):
    game = chess.Board(fen)
    return handle_bot(color, game)
