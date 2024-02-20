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
    chess.KING: INFINITY
}
TAKE_DRAW_WHEN_LOOSING_THRESHOLD = 7


def get_difference(game, color):
    if color == chess.BLACK:
        return get_current_score(game, chess.BLACK) - get_current_score(game, chess.WHITE)
    return get_current_score(game, chess.WHITE) - get_current_score(game, chess.BLACK)


def piece_table_score(score, color, game):
    if color == chess.WHITE:
        with open(Path('config/Piece-Square Tables/white.json'), 'r') as f:
            table = json.loads(f.read())
    else:
        with open(Path('config/Piece-Square Tables/black.json'), 'r') as f:
            table = json.loads(f.read())
    for Pawn in game.pieces(chess.PAWN, color):
        score += int(table["Pawn"][chess.square_rank(Pawn)][chess.square_file(Pawn)]) / 100
    for Knight in game.pieces(chess.KNIGHT, color):
        score += int(table["Knight"][chess.square_rank(Knight)][chess.square_file(Knight)]) / 100
    for Bishop in game.pieces(chess.BISHOP, color):
        score += int(table["Bishop"][chess.square_rank(Bishop)][chess.square_file(Bishop)]) / 100
    for Rook in game.pieces(chess.ROOK, color):
        score += int(table["Rook"][chess.square_rank(Rook)][chess.square_file(Rook)]) / 100
    for Queen in game.pieces(chess.QUEEN, color):
        score += int(table["Queen"][chess.square_rank(Queen)][chess.square_file(Queen)]) / 100
    for King in game.pieces(chess.KING, color):
        score += int(table["King"][chess.square_rank(King)][chess.square_file(King)]) / 100
    return score


def position_score(score, color, game):
    return piece_table_score(score, color, game)
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


def check_fork(game: chess.Board, score, color: chess.Color = chess.BLACK):
    best_score_rising = 0
    for pawn in game.pieces(chess.PAWN, color):  # todo En Passant
        con = 0
        if chess.square_file(pawn) in [0, 7]:
            continue
        else:
            checking_squares = [chess.square(chess.square_rank(pawn) - 1,
                                             chess.square_rank(pawn) + 1 if color == chess.WHITE else chess.square_rank(
                                                 pawn) - 1), chess.square(chess.square_rank(pawn) + 1,
                                                                          chess.square_rank(
                                                                              pawn) + 1 if color == chess.WHITE else chess.square_rank(
                                                                              pawn) - 1), ]
        for checking_square in checking_squares:
            if game.piece_at(checking_square) is not None and game.piece_at(
                    checking_square).color == get_opposite_color(color) and  chess.Move(pawn,
                                                                                           checking_square) in game.legal_moves:  # Checks if a pawn attacks a piece
                if len(game.attackers(color, checking_square)) == 0:#checks if there are no attackers todo check if pawn is defended wehn attacked
                    con += 1
            else:
                continue
        # Here it's a Fork (Both Forked pieces aren't defended)
        # Check if it makes sense to capture (Both pieces have higher values than the pawn)
        if con == 2:
            lowest_valuable_piece = (INFINITY, checking_squares[0])
            for checking_square in checking_squares:
                if PIECE_VALUES[game.piece_at(checking_square).piece_type] < lowest_valuable_piece[0]:
                    lowest_valuable_piece = (
                        PIECE_VALUES[game.piece_at(checking_square).piece_type],
                        checking_square)
            if lowest_valuable_piece[0] >= PIECE_VALUES[chess.PAWN]:
                best_score_rising = PIECE_VALUES[lowest_valuable_piece[0]] - PIECE_VALUES[chess.PAWN]
            if best_score_rising > 0:
                print(game.fen(), "Fork (Pawn)")
                game.push(chess.Move(pawn, lowest_valuable_piece[1]))
                print(f"New fen:{game.fen()} (Move:{chess.Move(pawn, lowest_valuable_piece[1])})")
                game.pop()

        """ for Knight in game.pieces(chess.KNIGHT, color):  # todo fork with king in check
        attacks = 0
        lowest_value_piece = (INFINITY, Knight)
        for attacked_square in game.attacks(Knight):
            if chess.Move(Knight, attacked_square) in game.legal_moves:
                game.push(chess.Move(Knight, attacked_square))
                in_danger = True
                if len(game.attackers(get_opposite_color(color), attacked_square)) == 0:
                    in_danger = False
                game.pop()
                if game.piece_at(attacked_square) is not None and (
                        (game.piece_at(attacked_square) in [chess.ROOK, chess.QUEEN, chess.KING]) or (
                not in_danger)):  # Higher value pieces or not defended

                    attacks += 1
                    if PIECE_VALUES[game.piece_at(attacked_square).piece_type] < lowest_value_piece[0]:
                        lowest_value_piece = (PIECE_VALUES[game.piece_at(attacked_square).piece_type], attacked_square)
        if attacks > 1:
            best_score_rising = lowest_value_piece[0]"""

    return score + best_score_rising


def check_passing_pawn(game, score, color=chess.BLACK):
    if len(game.pieces(chess.PAWN, color)) == 0:
        return score
    for my_piece_position in game.pieces(chess.PAWN, color):
        file = chess.square_file(my_piece_position)
        rank = chess.square_rank(my_piece_position)
        if file not in [0, 7]:
            files = [file - 1, file, file + 1]
        elif file == 0:
            files = [file, file + 1]
        elif file == 7:
            files = [file - 1, file]
        for scanning_file in files:
            for scanning_rank in range(rank, 8) if color == chess.WHITE else range(rank, 0, -1):
                if game.piece_at(chess.square(scanning_file, scanning_rank)) is not None and game.piece_at(
                        chess.square(scanning_file, scanning_rank)).piece_type == chess.PAWN and game.piece_at(
                    chess.square(scanning_file, scanning_rank)).color == get_opposite_color(color):
                    return score
        for scanning_rank in range(rank + 1, 8) if color == chess.WHITE else range(rank - 1, 0, -1):  # Double pawn
            if game.piece_at(chess.square(file, scanning_rank)) is not None and game.piece_at(
                    chess.square(file, scanning_rank)).piece_type == chess.PAWN and game.piece_at(
                chess.square(file, scanning_rank)).color == get_opposite_color(color):
                return score
    return score + 0.5


def get_opposite_color(color):
    if color == chess.WHITE:
        return chess.BLACK
    else:
        return chess.WHITE


def get_current_score(game, color=chess.BLACK, x=False):
    score = 0
    score += len(game.pieces(chess.PAWN, color)) * 1
    score += len(game.pieces(chess.BISHOP, color)) * 3
    score += len(game.pieces(chess.KNIGHT, color)) * 3
    score += len(game.pieces(chess.ROOK, color)) * 5
    score += len(game.pieces(chess.QUEEN, color)) * 9
    score = position_score(score, color, game)
    score = check_passing_pawn(game, score, color)
    score = check_fork(game, score, color)
    if game.outcome() is not None and game.outcome().winner == color:
        score += INFINITY
    elif game.outcome() is not None and game.outcome().winner == get_opposite_color(color):
        score -= INFINITY
    elif game.outcome() is not None and x == True and game.outcome().result() == "1/2-1/2" and score + TAKE_DRAW_WHEN_LOOSING_THRESHOLD < get_current_score(
            game,
            get_opposite_color(
                color), x=True):  # Check if it makes sense to draw
        score += INFINITY
    return score


def show_board_svg(game, SHOW_SVG=True):
    boardsvg = chess.svg.board(game, size=600, coordinates=True)
    with open('temp.svg', 'w') as outputfile:
        outputfile.write(boardsvg)
    time.sleep(0.1)
    if SHOW_SVG: os.startfile('temp.svg')


def handle_bot(my_color, game):
    if my_color == chess.WHITE:
        opponent_color = chess.BLACK
    else:
        opponent_color = chess.WHITE
    my_best_move_rating = -INFINITY
    for move_temp in game.legal_moves:
        first_possible_move = move_temp
        break
    my_best_moves = [first_possible_move]
    del first_possible_move
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
            possibles = []
            for number, entry in enumerate(reader.find_all(game)):
                possibles.append(entry.move)
                if number > 5:
                    break
            if len(possibles) > 0:
                return random.choice(possibles)
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
            if get_difference(game, opponent_color) > opponent_best_move_rating:
                opponent_best_move_rating = get_difference(game, opponent_color)
                opponent_best_move = opponent_move
            game.pop()
        game.push(opponent_best_move)
        if get_difference(game, my_color) > my_best_move_rating:
            my_best_move_rating = get_difference(game, my_color)
            my_best_moves = [my_move]
        elif get_difference(game, my_color) == my_best_move_rating:
            my_best_moves.append(my_move)
        game.pop()
        game.pop()
    my_best_move = random.choice(my_best_moves)
    return my_best_move


def generate_move(fen, color):
    game = chess.Board(fen)
    return handle_bot(color, game)
