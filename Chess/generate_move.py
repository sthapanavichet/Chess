from main import available_move, make_move, check_select
# flags for castling
castling_flags = {
    'K': True,      # white king's castling flag
    'KR': True,     # white right side castling flag
    'KL': True,     # white left side castling flag
    'k': True,      # black king's castling flag
    'kR': True,     # black right side castling flag
    'kL': True,     # black left side castling flag
}
# en_passant_flags
en_passant_flags = {      # en passant flags
    'a4': False, 'b4': False, 'c4': False, 'd4': False, 'e4': False, 'f4': False, 'g4': False, 'h4': False,
    'a5': False, 'b5': False, 'c5': False, 'd5': False, 'e5': False, 'f5': False, 'g5': False, 'h5': False,
}
# game starting position
starting_positions = {
    'e1': 'K', 'd1': 'Q', 'a1': 'R', 'h1': 'R', 'c1': 'B', 'f1': 'B', 'b1': 'N', 'g1': 'N',
    'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
    'e8': 'k', 'd8': 'q', 'a8': 'r', 'h8': 'r', 'c8': 'b', 'f8': 'b', 'b8': 'n', 'g8': 'n',
    'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p'
}
def get_white_moves(game_position):
    moves = {}
    for position in game_position:
        if game_position[position].isupper():
            moves[position] = available_move(position, game_position)
    return moves

def get_black_moves(game_position):
    moves = {}
    for position in game_position:
        if game_position[position].islower():
            moves[position] = available_move(position, game_position)
    return moves

