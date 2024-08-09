import sys
import pygame
import time
from timeit import default_timer as timer

# setup pygame
screen_width, screen_height = 600, 600
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chess")
# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
# move counter for the game, odd is white's turn, even is black's turn.
game_move_counter = 1
# positions of each squares
position_coord = {
    f'{letter}{number + 1}': [screen_width / 8 * letter_index + screen_width / 16,
                              screen_height / 8 * (8 - number) - screen_height / 16]
    for letter_index, letter in enumerate('abcdefgh') for number in range(8)
}
# extract sprites from sprite-sheet
sprite_sheet = pygame.image.load("2560px-Chess_Pieces_Sprite.svg.png")
sprite_column, sprite_row = 6, 2
sprite_width, sprite_height = sprite_sheet.get_width() / sprite_column, sprite_sheet.get_height() / sprite_row
sprite_rectangles = [
    pygame.Rect(sprite_sheet.get_width() * (i / sprite_column), sprite_sheet.get_height() * (j / sprite_row),
                sprite_width, sprite_height) for j in range(sprite_row) for i in range(sprite_column)
]
# rectangles defining where each sprite are on the sprites sheet
pieces = [sprite_sheet.subsurface(rect) for rect in sprite_rectangles]
# downsized_sprite (original is too big)
downsized_pieces = [pygame.transform.smoothscale(piece, (screen_width / 8, screen_height / 8)) for piece in pieces]
# dictionary for sprites of each chess piece
pieces_images = {
    'K': downsized_pieces[0],
    'Q': downsized_pieces[1],
    'B': downsized_pieces[2],
    'N': downsized_pieces[3],
    'R': downsized_pieces[4],
    'P': downsized_pieces[5],
    'k': downsized_pieces[6],
    'q': downsized_pieces[7],
    'b': downsized_pieces[8],
    'n': downsized_pieces[9],
    'r': downsized_pieces[10],
    'p': downsized_pieces[11],
}
# rectangles corresponding to each square on the board
square_rectangles = [pygame.Rect(screen_width / 8 * i, screen_height / 8 * (7 - j), screen_width / 8, screen_height / 8)
                     for i in range(8) for j in range(8)]
# history of all the game moves
game_moves = []     # index 0 = piece, 1-2 = move, 3-4 = original pos, 5 = move type
# flags for castling
castling_flag = {
    'K': True,      # white king's castling flag
    'KR': True,     # white right side castling flag
    'KL': True,     # white left side castling flag
    'k': True,      # black king's castling flag
    'kR': True,     # black right side castling flag
    'kL': True,     # black left side castling flag
}
# en_passant_flags
en_passant_flag = 0

# function to check if two pieces is the same color or not
def same_color(click_piece, selected_piece):
    return (click_piece.islower() and selected_piece.islower()) or (click_piece.isupper() and selected_piece.isupper())


# display the pieces on the board depending on their position
def display_pieces(game_position):
    for position in game_position:
        piece_image = pieces_images[game_position[position]]
        piece_rect = piece_image.get_rect()
        piece_rect.center = position_coord[position]
        screen.blit(piece_image, piece_rect)


# check if the piece selected is the right color or not
def check_select(selected_position, game_position):
    if selected_position in game_position:
        if game_move_counter % 2 == 1 and game_position[selected_position].isupper():  # white turn
            return True
        elif game_move_counter % 2 == 0 and game_position[selected_position].islower():  # black turn
            return True
    return False


# get the square that is clicked on
def get_square(mouse_x, mouse_y):
    for position, square_rect in zip(position_coord.items(), square_rectangles):
        if square_rect.collidepoint(mouse_x, mouse_y):
            return position[0]
    return None


# draw the chess board
def display_board():
    for j in range(8):
        for i in range(8):
            x_pos = i * (screen_width // 8)  # x position of the square
            y_pos = j * (screen_height // 8)  # y position of the square

            if (i + j) % 2 == 0:
                pygame.draw.rect(screen, GRAY, (x_pos, y_pos, screen_width / 8, screen_width / 8))
            else:
                pygame.draw.rect(screen, WHITE, (x_pos, y_pos, screen_width / 8, screen_width / 8))


def display_promotion_menu():
    font = pygame.font.Font(None, 36)
    text_surface = font.render("Choose a piece for promotion:", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height / 2 - 30))

    # Draw the menu background
    pygame.draw.rect(screen, (0, 0, 0), (screen_width / 4, screen_height / 4, screen_width / 2, screen_height / 2))
    screen.blit(text_surface, text_rect)

    # Load and draw promotion piece options
    promotion_choices = [pieces_images['Q'], pieces_images['R'], pieces_images['B'], pieces_images['N']]
    choice_rects = []

    for index, choice_image in enumerate(promotion_choices):
        choice_rect = choice_image.get_rect(center=(screen_width / 2, screen_height / 2 + index * 60))
        choice_rects.append((choice_image, choice_rect))
        screen.blit(choice_image, choice_rect)

    pygame.display.flip()

    return choice_rects

# Modify the pawn_promotion function
def pawn_promotion(selected_position, game_position):
    promotion_rank = '8' if game_position[selected_position[0:2]].isupper() else '1'

    if selected_position[1] == promotion_rank and game_position[selected_position[0:2]].lower() == 'p':
        promotion_menu_active = True
        choice_rects = display_promotion_menu()

        while promotion_menu_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for choice_image, rect in choice_rects:
                        if rect.collidepoint(mouse_x, mouse_y):
                            # Replace the pawn with the chosen piece
                            game_position[selected_position[0:2]] = 'Q'  # Replace with actual conversion logic
                            promotion_menu_active = False
                            break

        # Display the updated board after promotion
        display_board()
        display_pieces(game_position)
        pygame.display.flip()


# make a move by changing the game position dictionary
def make_move(original_position, selected_position, game_position, castling_flags):
    global en_passant_flag
    en_passant_flag = 0
    piece = game_position[original_position]
    if selected_position[2] == '1':     # normal move
        if castling_flags['K']:
            if original_position == 'a1' or selected_position == 'a1':
                castling_flags['KL'] = False
            elif original_position == 'h1' or selected_position == 'h1':
                castling_flags['KR'] = False
        if castling_flags['k']:
            if original_position == 'a8' or selected_position == 'a8':
                castling_flags['kL'] = False
            elif original_position == 'h8' or selected_position == 'h8':
                castling_flags['kR'] = False
        if piece == 'K' or piece == 'k':
            castling_flags[piece] = False
        if piece == 'P' or piece == 'p':
            if (selected_position[1] == '4' and original_position[1] == '2') or (selected_position[1] == '5' and original_position[1] == '7'):
                en_passant_flag = selected_position[0:2]
            if selected_position[1] == '8' or selected_position[1] == '1':
                pawn_promotion(selected_position, game_position)
    elif selected_position[2] == '2':     # en passant
        if piece.isupper():
            game_position.pop(selected_position[0] + '5')
        else:
            game_position.pop(selected_position[0] + '4')
    else:      # castling
        if piece.isupper():
            if selected_position[0:2] == 'c1':
                game_position['d1'] = game_position.pop('a1')
            elif selected_position[0:2] == 'g1':
                game_position['f1'] = game_position.pop('h1')
        else:
            if selected_position[0:2] == 'c8':
                game_position['d8'] = game_position.pop('a8')
            elif selected_position[0:2] == 'g8':
                game_position['f8'] = game_position.pop('h8')
    game_position[selected_position[0:2]] = game_position.pop(original_position)


# move piece to its desired position on the board
def move_piece(original_position, selected_position, game_position, castling_flags):
    global en_passant_flag
    move = f"{game_position[original_position]}{original_position}{selected_position}"
    game_moves.append(move)
    make_move(original_position, selected_position, game_position, castling_flags)
    display_board()
    display_pieces(game_position)
    pygame.display.flip()
    # time.sleep(1)


# draw positions onto the board
def print_position(game_position):
    font = pygame.font.Font(None, 36)  # None uses the default system font, size 36
    for key, value in position_coord.items():
        if key in game_position:
            text_surface = font.render(key, True, (0, 255, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = (value[0], value[1])
            screen.blit(text_surface, text_rect)
    pygame.display.flip()


# get the available moves of a pawn
def pawn_move(position, game_position):
    global en_passant_flag
    columns = 'abcdefgh'
    col, row = position[0], int(position[1])
    current_index = columns.index(col)
    threats = []
    available_moves = []
    if game_position[position].isupper():
        pawn_threats = [(1, 1), (-1, 1)]
    else:
        pawn_threats = [(1, -1), (-1, -1)]
    for pawn_threat in pawn_threats:  # check for valid moves in the possible moves
        if 0 <= current_index + pawn_threat[0] < 8 and 1 <= row + pawn_threat[1] <= 8:
            move = columns[current_index + pawn_threat[0]] + str(row + pawn_threat[1])
            threats.append(move)
    # add threats to available moves if there is an enemy piece on the position
    for threat in threats:
        if threat in game_position:
            if not same_color(game_position[position], game_position[threat]):
                available_moves.append(threat + '1')
    if game_position[position].isupper():  # white pawn
        if position[1] == '2':  # double move
            for i in range(1, 3):
                move = col + str(row + i)
                if move in game_position:
                    break
                available_moves.append(move+'1')
        else:
            if position[1] == '5':  # en passant
                if en_passant_flag != 0:
                    right_square = columns[current_index + 1] + str(row) if current_index + 1 <= 7 else None
                    left_square = columns[current_index - 1] + str(row) if current_index - 1 >= 0 else None
                    for square in [right_square, left_square]:
                        if square in game_position:
                            if game_position[square].islower():
                                if en_passant_flag == square:
                                    move = square[0] + '6'
                                    available_moves.append(move + '2')
            move = col + str(row + 1)   # normal pawn move
            if move not in game_position:
                available_moves.append(move + '1')
    else:  # black pawn
        if position[1] == '7':  # double move
            for i in range(1, 3):
                move = col + str(row - i)
                if move in game_position:
                    break
                available_moves.append(move+'1')
        else:
            if position[1] == '4':  # en passant
                if en_passant_flag != 0:
                    right_square = columns[current_index + 1] + str(row) if current_index + 1 <= 7 else None
                    left_square = columns[current_index - 1] + str(row) if current_index - 1 >= 0 else None
                    for square in [right_square, left_square]:
                        if square in game_position:
                            if game_position[square].islower():
                                if en_passant_flag == square:
                                    move = square[0] + '3'
                                    available_moves.append(move + '2')
            move = col + str(row - 1)   # normal pawn move
            if move not in game_position:
                available_moves.append(move+'1')
    return available_moves, threats


# get the available moves of a rook
def rook_move(position, game_position):
    columns = 'abcdefgh'
    col, row = position[0], int(position[1])
    current_index = columns.index(col)
    available_moves = []
    threats = []
    while current_index < len(columns) - 1:  # moves in pos x direction
        current_index += 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    current_index = columns.index(col)
    while current_index > 0:  # moves in the neg x direction
        current_index -= 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:   # stops when it sees another piece
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    while row < 8:  # moves in the pos y direction
        row += 1
        move = col + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    row = int(position[1])
    while row > 1:  # moves in the neg y direction
        row -= 1
        move = col + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    return available_moves, threats


# get the available moves of a bishop
def bishop_move(position, game_position):
    columns = 'abcdefgh'
    col, row = position[0], int(position[1])
    current_index = columns.index(col)
    available_moves = []
    threats = []
    while current_index < len(columns) - 1 and row < 8:  # moves in the top right diagonal
        current_index += 1
        row += 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    row = int(position[1])
    current_index = columns.index(col)
    while current_index < len(columns) - 1 and row > 1:  # moves in the lower right diagonal
        current_index += 1
        row -= 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    row = int(position[1])
    current_index = columns.index(col)
    while current_index > 0 and row < 8:  # moves in the upper left diagonal
        current_index -= 1
        row += 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    row = int(position[1])
    current_index = columns.index(col)
    while current_index > 0 and row > 1:  # moves in the lower left diagonal
        current_index -= 1
        row -= 1
        move = columns[current_index] + str(row)
        threats.append(move)
        if move in game_position:
            if not same_color(game_position[move], game_position[position]):
                available_moves.append(move+'1')
            break
        available_moves.append(move+'1')
    return available_moves, threats


# get the available moves of a knight
def knight_move(position, game_position):
    columns = 'abcdefgh'
    col, row = position[0], int(position[1])
    current_index = columns.index(col)
    available_moves = []
    threats = []
    # possible knight moves relative to its position (x, y)
    knight_moves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
    for Knight_move in knight_moves:  # check for valid moves in the possible moves
        if 0 <= current_index + Knight_move[0] < 8 and 1 <= row + Knight_move[1] <= 8:
            move = columns[current_index + Knight_move[0]] + str(row + Knight_move[1])
            threats.append(move)
            if move in game_position:
                if not same_color(game_position[move], game_position[position]):
                    available_moves.append(move+'1')
            else:
                available_moves.append(move + '1')
    return available_moves, threats


# get the threats of the king
def king_threat(position):
    columns = 'abcdefgh'
    col, row = position[0], int(position[1])
    current_index = columns.index(col)
    threats = []

    # possible king moves relative to its position (x, y)
    king_moves = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    for King_move in king_moves:
        if 0 <= current_index + King_move[0] < 8 and 1 <= row + King_move[1] <= 8:
            move = columns[current_index + King_move[0]] + str(row + King_move[1])
            threats.append(move)
    return threats


# calculate the threats of white pieces
def get_white_threats(game_position):
    white_threats = []
    for piece_position in game_position:
        if game_position[piece_position].isupper():
            if game_position[piece_position] == 'K':
                white_threats.extend(king_threat(piece_position))
            else:
                white_threats.extend(possible_move(piece_position, game_position, castling_flag)[1])
    return white_threats


# calculate the threats of black pieces
def get_black_threats(game_position):
    black_threats = []
    for piece_position in game_position:
        if game_position[piece_position].islower():
            if game_position[piece_position] == 'k':
                black_threats.extend(king_threat(piece_position))
            else:
                black_threats.extend(possible_move(piece_position, game_position, castling_flag)[1])
    return black_threats


# get the available moves of the king
def king_move(position, game_position, castling_flags):
    threats = king_threat(position)
    available_moves = []
    if game_position[position].isupper():  # white king
        black_threats = get_black_threats(game_position)
        for move in threats:  # exclude moves that put the king in any danger
            if move not in black_threats:
                if move in game_position:
                    if game_position[move].islower():
                        available_moves.append(move+'1')
                else:
                    available_moves.append(move+'1')
        if castling_flags['K']:
            if castling_flags['KR']:
                if 'f11' in available_moves and 'g1' not in game_position:
                    if 'g1' not in black_threats:
                        available_moves.append('g13')
            if castling_flags['KL']:
                if 'b1' not in game_position and 'c1' not in game_position and 'd11' in available_moves:
                    if 'b1' not in black_threats and 'c1' not in black_threats:
                        available_moves.append('c13')
    else:  # black king
        white_threats = get_white_threats(game_position)
        for move in threats:    # exclude moves that put the king in any danger
            if move not in white_threats:
                if move in game_position:
                    if game_position[move].isupper():
                        available_moves.append(move+'1')
                else:
                    available_moves.append(move+'1')
        if castling_flags['k']:
            if castling_flags['kR']:
                if 'f81' in available_moves and 'g8' not in game_position:
                    if 'g8' not in white_threats:
                        available_moves.append('g83')
            if castling_flags['kL']:
                if 'b8' not in game_position and 'c8' not in game_position and 'd81' in available_moves:
                    if 'b8' not in white_threats and 'c8' not in white_threats:
                        available_moves.append('c83')
    return available_moves


# check if the king is in check or not
def in_check(game_position, move_counter):
    if move_counter % 2 == 1:
        black_threats = get_black_threats(game_position)
        for position, piece in game_position.items():
            if piece == 'K':
                if position in black_threats:
                    return position
    else:
        white_threats = get_white_threats(game_position)
        for position, piece in game_position.items():
            if piece == 'k':
                if position in white_threats:
                    return position
    return None


# get the available moves of any pieces
def possible_move(selected_position, game_position, castling_flags):
    global en_passant_flag
    piece = game_position[selected_position]
    if piece == 'P' or piece == 'p':
        return pawn_move(selected_position, game_position)
    elif piece == 'N' or piece == 'n':
        return knight_move(selected_position, game_position)
    elif piece == 'R' or piece == 'r':
        return rook_move(selected_position, game_position)
    elif piece == 'B' or piece == 'b':
        return bishop_move(selected_position, game_position)
    elif piece == 'Q' or piece == 'q':
        possible_moves, threats = bishop_move(selected_position, game_position)
        possible_moves.extend(rook_move(selected_position, game_position)[0])
        threats.extend(rook_move(selected_position, game_position)[1])
        return possible_moves, threats
    else:
        return king_move(selected_position, game_position, castling_flags), king_threat(selected_position)


def try_move(original_position, selected_position, game_position):
    piece = game_position[original_position]
    if selected_position[2] == '2':     # en passant
        if piece.isupper():
            game_position.pop(selected_position[0] + '5')
        else:
            game_position.pop(selected_position[0] + '4')
    elif selected_position[2] == '3':      # castling
        if piece.isupper():
            if selected_position[0:2] == 'c1':
                game_position['d1'] = game_position.pop('a1')
            elif selected_position[0:2] == 'g1':
                game_position['f1'] = game_position.pop('h1')
        else:
            if selected_position[0:2] == 'c8':
                game_position['d8'] = game_position.pop('a8')
            elif selected_position[0:2] == 'g8':
                game_position['f8'] = game_position.pop('h8')
    game_position[selected_position[0:2]] = game_position.pop(original_position)

# get the available moves of any piece when their king is in check
def available_move(selected_position, game_position, castling_flags, move_counter):
    en_passant = en_passant_flag
    available_moves = []
    # try all the possible moves and see if the king is still in check, if not add it to the available moves
    possible_moves = possible_move(selected_position, game_position, castling_flags)[0]
    for move in possible_moves:
        game_copy = game_position.copy()
        try_move(selected_position, move, game_copy)
        if in_check(game_copy, move_counter) is None:
            available_moves.append(move)
    return available_moves


# draw the available moves on the board
def draw_available_moves(available_moves, game_position):
    display_board()
    display_pieces(game_position)
    for move in available_moves:
        square_center = position_coord[move[0:2]]
        pygame.draw.circle(screen, (192, 192, 192), square_center, 10)


def is_checkmate(king_position, game_position, move_counter):
    global en_passant_flag
    king_moves = king_move(king_position, game_position, castling_flag)
    if king_moves:
        return False
    for position in game_position:
        if same_color(game_position[position], game_position[king_position]):
            available_moves = available_move(position, game_position, castling_flag, move_counter)
            if available_moves:
                return False
    return True


def get_moves(game_position, move_counter, castling_flags):
    global en_passant_flag
    moves = {}
    if move_counter % 2 == 1:
        for position in game_position:
            if game_position[position].isupper():
                moves[position] = available_move(position, game_position, castling_flags, move_counter)
    else:
        for position in game_position:
            if game_position[position].islower():
                moves[position] = available_move(position, game_position, castling_flags, move_counter)
    return moves


def generate_position(max_depth, depth, game_position, castling, en_passant, move_counter):
    if depth > max_depth:
        return 0
    else:
        move_num = 0
        moves = get_moves(game_position, move_counter, castling)
        for position in moves:
            for move in moves[position]:
                move_num += 1
                game_copy = game_position.copy()
                castling_copy = castling.copy()
                # move_piece(position, move, game_copy, castling_copy)
                make_move(position, move, game_copy, castling_copy)
                check = in_check(game_copy, move_counter)
                if check:
                    if not is_checkmate(check, game_copy, move_counter):
                        move_num += generate_position(max_depth, depth + 1, game_copy, castling, en_passant,
                                                      move_counter + 1)
                    else:
                        print(1)
                else:
                    move_num += generate_position(max_depth, depth + 1, game_copy, castling, en_passant,
                                                  move_counter + 1)
    return move_num











def main():
    global game_move_counter
    color_dict = {1: 'White', 0: 'Black'}
    # game starting position
    starting_positions = {
        'e1': 'K', 'd1': 'Q', 'a1': 'R', 'h1': 'R', 'c1': 'B', 'f1': 'B', 'b1': 'N', 'g1': 'N',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
        'e8': 'k', 'd8': 'q', 'a8': 'r', 'h8': 'r', 'c8': 'b', 'f8': 'b', 'b8': 'n', 'g8': 'n',
        'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p'
    }

    display_board()
    display_pieces(starting_positions)
    pygame.display.flip()

    selected_position = None
    game_position = starting_positions.copy()

    running = True
    check = None
    available_moves = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check which square is clicked
                mouse_x, mouse_y = pygame.mouse.get_pos()
                click_position = get_square(mouse_x, mouse_y)
                if check_select(click_position, game_position):
                    selected_position = click_position
                    available_moves = available_move(selected_position, game_position, castling_flag, game_move_counter)
                    draw_available_moves(available_moves, game_position)
                else:
                    if selected_position is not None:
                        for move in available_moves:
                            if click_position == move[0:2]:
                                move_piece(selected_position, move, game_position, castling_flag)
                                selected_position = None
                                game_move_counter += 1
                        check = in_check(game_position, game_move_counter)
                # check for mate
                if check:
                    if is_checkmate(check, game_position, game_move_counter):
                        font = pygame.font.Font(None, 36)
                        text_surface = font.render(f"Checkmate! {color_dict[game_move_counter % 2]} Lost",
                                                   True, (0, 255, 0))
                        text_rect = text_surface.get_rect()
                        text_rect.center = (screen_width / 2, screen_height / 2)
                        screen.blit(text_surface, text_rect)
                    else:
                        square_center = position_coord[check]
                        pygame.draw.circle(screen, (255, 0, 0), square_center, 10)
                pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()

test_position = {
        'e1': 'K', 'd1': 'Q', 'a1': 'R', 'h1': 'R', 'c1': 'B', 'f1': 'B', 'b1': 'N', 'g1': 'N',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
        'e8': 'k', 'd8': 'q', 'a8': 'r', 'h8': 'r', 'c8': 'b', 'f8': 'b', 'b8': 'n', 'g8': 'n',
        'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p'
    }

if __name__ == '__main__':
    start = timer()
    print(generate_position(4, 1, test_position, castling_flag, en_passant_flag, 1))
    print(timer() - start)
    pygame.quit()
    sys.exit()
    # main()