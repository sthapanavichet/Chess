# font = pygame.font.Font(None, 36)  # None uses the default system font, size 36
# for key, value in position_coord.items():
#
#     text_surface = font.render(key, True, RED)
#
#     text_rect = text_surface.get_rect()
#
#     text_rect.center = (value[0], value[1])
#
#     screen.blit(text_surface, text_rect)
#     print(f'{key}: {value}')
from timeit import default_timer as timer
from time import sleep
import pygame
import sys

# setup pygame
screen_width, screen_height = 600, 600
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chess")
# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
# positions of each squares
position_coord = {
    (col+1) * 10 + row + 1: [screen_width / 8 * col + screen_width / 16, screen_height / 8 * (8 - row) - screen_height / 16]
    for col in range(8) for row in range(8)
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
white_pieces_images = {
    1: downsized_pieces[0],
    2: downsized_pieces[1],
    3: downsized_pieces[4],
    4: downsized_pieces[2],
    5: downsized_pieces[3],
    6: downsized_pieces[5],
}
black_pieces_images = {
    1: downsized_pieces[6],
    2: downsized_pieces[7],
    3: downsized_pieces[10],
    4: downsized_pieces[8],
    5: downsized_pieces[9],
    6: downsized_pieces[11],
}
square_rectangles = [pygame.Rect(screen_width / 8 * row, screen_height / 8 * (7 - col), screen_width / 8, screen_height / 8)
                     for row in range(8) for col in range(8)]

piece_value = {
            1: 0,
            2: 10,
            3: 5,
            4: 3,
            5: 3,
            6: 1
        }

def get_square(mouse_x, mouse_y):
    for position, square_rect in zip(position_coord.keys(), square_rectangles):
        if square_rect.collidepoint(mouse_x, mouse_y):
            return position
    return None


# draw the chess board
def display_board():
    for row in range(8):
        for col in range(8):
            x_pos = col * (screen_width // 8)  # x position of the square
            y_pos = row * (screen_height // 8)  # y position of the square

            if (col + row) % 2 == 0:
                pygame.draw.rect(screen, GRAY, (x_pos, y_pos, screen_width / 8, screen_width / 8))
            else:
                pygame.draw.rect(screen, WHITE, (x_pos, y_pos, screen_width / 8, screen_width / 8))

def print_position(game_position):
    font = pygame.font.Font(None, 36)  # None uses the default system font, size 36
    for key, value in position_coord.items():
        if key in game_position:
            # text_surface = font.render(str(key), True, (0, 255, 0))
            text_surface = font.render(str(game_position[key]), True, (0, 255, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = (value[0], value[1])
            screen.blit(text_surface, text_rect)
    pygame.display.flip()


class Board:
    # K = 1
    # Q = 2
    # R = 3
    # B = 4
    # K = 5
    # P = 6
    # white_position = {
    #     51: 1, 41: 2, 11: 3, 81: 3, 31: 4, 61: 4, 21: 5, 71: 5,
    #     12: 6, 22: 6, 32: 6, 42: 6, 52: 6, 62: 6, 72: 6, 82: 6
    # }
    # 'e1': 'K', 'd1': 'Q', 'a1': 'R', 'h1': 'R', 'c1': 'B', 'f1': 'B', 'b1': 'N', 'g1': 'N',
    # 'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P'
    # black_position = {
    #     58: 1, 48: 2, 18: 3, 88: 3, 38: 4, 68: 4, 28: 5, 78: 5,
    #     17: 6, 27: 6, 37: 6, 47: 6, 57: 6, 67: 6, 77: 6, 87: 6
    # }
    # 'e8': 'k', 'd8': 'q', 'a8': 'r', 'h8': 'r', 'c8': 'b', 'f8': 'b', 'b8': 'n', 'g8': 'n',
    # 'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p'
    castling_flags = {
        1: True,      # white king's castling flag
        11: True,     # white right side castling flag
        12: True,     # white left side castling flag
        2: True,      # black king's castling flag
        21: True,     # black right side castling flag
        22: True,     # black left side castling flag
    }

    en_passant_flag = 0
    move_counter = 0

    def __init__(self, white_position, black_position, castling_flags=None, en_passant_flag=0, move_counter=0):
        self.white_position = white_position.copy()
        self.black_position = black_position.copy()

        if castling_flags:
            self.castling_flags = castling_flags.copy()
        self.en_passant_flag = en_passant_flag
        self.move_counter = move_counter

    def display_pieces(self):
        for position, piece in self.white_position.items():
            piece_image = white_pieces_images[piece]
            piece_rect = piece_image.get_rect()
            piece_rect.center = position_coord[position]
            screen.blit(piece_image, piece_rect)
        for position, piece in self.black_position.items():
            piece_image = black_pieces_images[piece]
            piece_rect = piece_image.get_rect()
            piece_rect.center = position_coord[position]
            screen.blit(piece_image, piece_rect)


    def check_select(self, position):
        if self.move_counter % 2 == 0:
            return position in self.white_position
        else:
            return position in self.black_position

    # get the square that is clicked on


    def copy(self):
        return Board(self.white_position, self.black_position, self.castling_flags, self.en_passant_flag, self.move_counter)

    def make_move(self, position, move):
        self.en_passant_flag = 0
        if self.move_counter % 2 == 0:
            piece = self.white_position[position]
            if piece == 1:
                self.castling_flags[1] = False
            if move // 100 == 0:
                if self.castling_flags[1]:
                    if position == 11 or move == 11:
                        self.castling_flags[12] = False
                    elif position == 81 or move == 81:
                        self.castling_flags[11] = False
                if piece == 6:
                    if position % 10 == 2 and move % 10 == 4:
                        self.en_passant_flag = move
            elif move // 100 == 2:
                move %= 200
                self.black_position.pop(move-1)
            else:
                if move == 331:
                    move = 31
                    self.white_position[41] = self.white_position.pop(11)
                else:
                    move = 71
                    self.white_position[61] = self.white_position.pop(81)
            self.white_position[move] = self.white_position.pop(position)
            if move in self.black_position:
                self.black_position.pop(move)
        else:
            piece = self.black_position[position]
            if piece == 1:
                self.castling_flags[2] = False
            if move // 100 == 0:
                if self.castling_flags[2]:
                    if position == 18 or move == 18:
                        self.castling_flags[22] = False
                    elif position == 88 or move == 88:
                        self.castling_flags[21] = False
                if piece == 6:
                    if position % 10 == 7 and move % 10 == 5:
                        self.en_passant_flag = move
            elif move // 100 == 2:
                move %= 200
                self.white_position.pop(move+1)
            else:
                if move == 338:
                    move = 38
                    self.black_position[48] = self.black_position.pop(18)

                else:
                    move = 78
                    self.black_position[68] = self.black_position.pop(88)
            self.black_position[move] = self.black_position.pop(position)
            if move in self.white_position:
                self.white_position.pop(move)
        self.move_counter += 1

    def try_move(self, position, move):
        game_copy = self.copy()
        if self.move_counter % 2 == 0:
            if move // 100 == 2:
                move -= 199
            elif move // 100 == 3:
                if move == 331:
                    move = 31
                    game_copy.white_position[41] = game_copy.white_position.pop(11)
                else:
                    move = 71
                    game_copy.white_position[61] = game_copy.white_position.pop(81)
            game_copy.white_position[move] = game_copy.white_position.pop(position)
            if move in game_copy.black_position:
                game_copy.black_position.pop(move)
            if game_copy.in_check():
                return True
        else:
            if move // 100 == 2:
                move -= 201
            elif move // 100 == 3:
                if move == 338:
                    move = 38
                    game_copy.black_position[48] = game_copy.black_position.pop(18)
                else:
                    move = 78
                    game_copy.black_position[68] = game_copy.black_position.pop(88)
            game_copy.black_position[move] = game_copy.black_position.pop(position)
            if move in game_copy.white_position:
                game_copy.white_position.pop(move)
            if game_copy.in_check():
                return True
        return False

    # move piece to its desired position on the board
    def move_piece(self, position, move):
        self.make_move(position, move)
        display_board()
        self.display_pieces()
        pygame.display.flip()

    def white_pawn_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        pawn_threats = [(1, 1), (-1, 1)]
        for pawn_threat in pawn_threats:  # check for valid moves in the possible moves
            if 0 < col + pawn_threat[0] <= 8 and row < 8:
                move = (col + pawn_threat[0]) * 10 + row + pawn_threat[1]
                threats.append(move)
        return threats

    def black_pawn_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        pawn_threats = [(1, -1), (-1, -1)]
        for pawn_threat in pawn_threats:  # check for valid moves in the possible moves
            if 1 <= col + pawn_threat[0] <= 8 and row > 1:
                move = (col + pawn_threat[0]) * 10 + row + pawn_threat[1]
                threats.append(move)
        return threats

    def piece(self, position):
        return position in self.white_position or position in self.black_position
    def pawn_move(self, position):
        col, row = position // 10, position % 10
        available_moves = []
        if self.move_counter % 2 == 0:
            pawn_threats = self.white_pawn_threat(position)
            for pawn_threat in pawn_threats:  # check for valid moves in the possible moves
                # add threats to available moves if there is an enemy piece on the position
                if pawn_threat in self.black_position:
                    available_moves.append(pawn_threat)
            if row == 2:
                for i in range(1, 3):
                    move = col * 10 + row + i
                    if self.piece(move):
                        break
                    available_moves.append(move)
            else:
                if row == 5:  # en passant
                    if self.en_passant_flag != 0:
                        # right_square = (col + 1) * 10 + row if col + 1 <= 8 else None
                        # left_square = (col - 1) * 10 + row if col - 1 >= 0 else None
                        squares = [(col + 1) * 10 + row if col + 1 <= 8 else None, (col - 1) * 10 + row if col - 1 >= 0 else None]
                        for square in squares:
                            if self.en_passant_flag == square:
                                move = 200 + square - row + 6
                                available_moves.append(move)
                                break
                move = col * 10 + row + 1  # normal pawn move
                if not self.piece(move):
                    available_moves.append(move)
        else:
            pawn_threats = self.black_pawn_threat(position)
            for pawn_threat in pawn_threats:  # check for valid moves in the possible moves
                # add threats to available moves if there is an enemy piece on the position
                if pawn_threat in self.white_position:
                    available_moves.append(pawn_threat)
            if row == 7:
                for i in range(1, 3):
                    move = col * 10 + row - i
                    if self.piece(move):
                        break
                    available_moves.append(move)
            else:
                if row == 4:  # en passant
                    if self.en_passant_flag != 0:
                        # right_square = (col + 1) * 10 + row if col + 1 <= 8 else None
                        # left_square = (col - 1) * 10 + row if col - 1 >= 0 else None
                        squares = [(col + 1) * 10 + row if col + 1 <= 8 else None, (col - 1) * 10 + row if col - 1 >= 0 else None]
                        for square in squares:
                            if self.en_passant_flag == square:
                                move = 200 + square - row + 3
                                available_moves.append(move)
                                break
                move = col * 10 + row - 1  # normal pawn move
                if not self.piece(move):
                    available_moves.append(move)
        return available_moves

    def enemy(self, position):
        if self.move_counter % 2 == 0:
            return position in self.black_position
        else:
            return position in self.white_position

    def ally(self, position):
        if self.move_counter % 2 == 0:
            return position in self.white_position
        else:
            return position in self.black_position

    def rook_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        while row < 8:  # moves in pos y direction
            row += 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        row = position % 10
        while row > 1:  # moves in neg y direction
            row -= 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        row = position % 10
        while col < 8:  # moves in the pos x direction
            col += 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        col = position // 10
        while col > 1:  # moves in the neg x direction
            col -= 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break
        return threats

    def rook_move(self, position):
        col, row = position // 10, position % 10
        available_moves = []
        while row < 8:  # moves in pos y direction
            row += 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        row = position % 10
        while row > 1:  # moves in neg y direction
            row -= 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        row = position % 10
        while col < 8:  # moves in the pos x direction
            col += 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        col = position // 10
        while col > 1:  # moves in the neg x direction
            col -= 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)
        return available_moves

    def bishop_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        while col < 8 and row < 8:  # moves in the top right diagonal
            col += 1
            row += 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        col, row = position // 10, position % 10
        while col < 8 and row > 1:  # moves in the lower right diagonal
            col += 1
            row -= 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        col, row = position // 10, position % 10
        while col > 1 and row < 8:  # moves in the upper left diagonal
            col -= 1
            row += 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break

        col, row = position // 10, position % 10
        while col > 1 and row > 1:  # moves in the lower left diagonal
            col -= 1
            row -= 1
            move = col * 10 + row
            threats.append(move)
            if self.piece(move):
                break
        return threats

    # get the available moves of a bishop
    def bishop_move(self, position):
        col, row = position // 10, position % 10
        available_moves = []
        while col < 8 and row < 8:  # moves in the top right diagonal
            col += 1
            row += 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        col, row = position // 10, position % 10
        while col < 8 and row > 1:  # moves in the lower right diagonal
            col += 1
            row -= 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        col, row = position // 10, position % 10
        while col > 1 and row < 8:  # moves in the upper left diagonal
            col -= 1
            row += 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)

        col, row = position // 10, position % 10
        while col > 1 and row > 1:  # moves in the lower left diagonal
            col -= 1
            row -= 1
            move = col * 10 + row
            if self.enemy(move):
                available_moves.append(move)
                break
            elif self.ally(move):
                break
            available_moves.append(move)
        return available_moves
    
    def knight_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        # possible knight moves relative to its position (x, y)
        knight_moves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
        for knight_move in knight_moves:  # check for valid moves in the possible moves
            if 1 <= col + knight_move[0] <= 8 and 1 <= row + knight_move[1] <= 8:
                move = (col + knight_move[0]) * 10 + row + knight_move[1]
                threats.append(move)
        return threats
    
    # get the available moves of a knight
    def knight_move(self, position):
        available_moves = []
        # possible knight moves relative to its position (x, y)
        knight_threats = self.knight_threat(position) 
        for knight_threat in knight_threats:  # check for valid moves in the possible moves
            if not self.ally(knight_threat):
                available_moves.append(knight_threat)
        return available_moves

    def king_threat(self, position):
        col, row = position // 10, position % 10
        threats = []
        # possible king moves relative to its position (x, y)
        king_moves = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        for king_move in king_moves:
            if 1 <= col + king_move[0] <= 8 and 1 <= row + king_move[1] <= 8:
                move = (col + king_move[0]) * 10 + row + king_move[1]
                threats.append(move)
        return threats

    def white_threat(self, position):
        piece = self.white_position[position]
        if piece == 6:
            return self.white_pawn_threat(position)
        elif piece == 2:
            ret = self.rook_threat(position)
            ret.extend(self.bishop_threat(position))
            return ret
        elif piece == 3:
            return self.rook_threat(position)
        elif piece == 4:
            return self.bishop_threat(position)
        elif piece == 5:
            return self.knight_threat(position)
        else:
            return self.king_threat(position)

    def get_white_threats(self):
        white_threats = []
        for position, piece in self.white_position.items():
            if piece != 0:
                white_threats.extend(self.white_threat(position))
        return white_threats

    def black_threat(self, position):
        piece = self.black_position[position]

        if piece == 6:
            return self.black_pawn_threat(position)
        elif piece == 2:
            ret = self.rook_threat(position)
            ret.extend(self.bishop_threat(position))
            return ret
        elif piece == 3:
            return self.rook_threat(position)
        elif piece == 4:
            return self.bishop_threat(position)
        elif piece == 5:
            return self.knight_threat(position)
        else:
            return self.king_threat(position)

    def get_black_threats(self):
        black_threats = []
        for position, piece in self.black_position.items():
            if piece != 0:
                black_threats.extend(self.black_threat(position))
        return black_threats

    def king_move(self, position):
        threats = self.king_threat(position)
        available_moves = []
        if self.move_counter % 2 == 0:  # white king
            black_threats = self.get_black_threats()
            for threat in threats:  # exclude moves that put the king in any danger
                if threat not in black_threats:
                    if self.ally(threat):
                        continue
                    available_moves.append(threat)
            if self.castling_flags[1]:
                if self.castling_flags[11]:  # right side castling
                    if 61 in available_moves and not self.piece(71):
                        if 71 not in black_threats:
                            available_moves.append(371)
                if self.castling_flags[12]:  # left side castling
                    if not self.piece(21) and not self.piece(31) and 41 in available_moves:
                        if 21 not in black_threats and 31 not in black_threats:
                            available_moves.append(331)
        else:  # black king
            white_threats = self.get_white_threats()
            for threat in threats:  # exclude moves that put the king in any danger
                if threat not in white_threats:
                    if self.ally(threat):
                        continue
                    available_moves.append(threat)
            if self.castling_flags[2]:
                if self.castling_flags[21]:  # right side castling
                    if 68 in available_moves and not self.piece(78):
                        if 78 not in white_threats:
                            available_moves.append(378)
                if self.castling_flags[22]:  # left side castling
                    if not self.piece(28) and not self.piece(38) and 48 in available_moves:
                        if 28 not in white_threats and 38 not in white_threats:
                            available_moves.append(338)
        return available_moves

    def in_check(self):
        if self.move_counter % 2 == 0:
            black_threats = self.get_black_threats()
            for black_threat in black_threats:
                if black_threat in self.white_position and self.white_position[black_threat] == 1:
                    return black_threat
        else:
            white_threats = self.get_white_threats()
            for white_threat in white_threats:
                if white_threat in self.black_position and self.black_position[white_threat] == 1:
                    return white_threat
        return None

    def possible_move(self, position):
        piece = None
        if self.move_counter % 2 == 0:
            piece = self.white_position[position]
        else:
            piece = self.black_position[position]
        if piece == 6:
            return self.pawn_move(position)
        elif piece == 5:
            return self.knight_move(position)
        elif piece == 4:
            return self.bishop_move(position)
        elif piece == 3:
            return self.rook_move(position)
        elif piece == 2:
            ret = self.rook_move(position)
            ret.extend(self.bishop_move(position))
            return ret
        else:
            return self.king_move(position)



    def available_move(self, position):
        available_moves = []
        # try all the possible moves and see if the king is still in check, if not add it to the available moves
        possible_moves = self.possible_move(position)
        for move in possible_moves:
            if not self.try_move(position, move):
                available_moves.append(move)
        return available_moves

    def is_checkmate(self, king_position,):
        king_moves = self.king_move(king_position)
        if king_moves:
            return False
        if self.move_counter % 2 == 0:
            for position, piece in self.white_position.items():
                if piece != 0:
                    available_moves = self.available_move(position)
                    if available_moves:
                        return False
        else:
            for position, piece in self.black_position.items():
                if piece != 0:
                    available_moves = self.available_move(position)
                    if available_moves:
                        return False
        return True

    def draw_available_moves(self, available_moves):
        display_board()
        self.display_pieces()
        for move in available_moves:
            square_center = position_coord[move % 100]
            pygame.draw.circle(screen, (192, 192, 192), square_center, 10)

    def generate_position(self, max_depth, depth):
        if depth > max_depth:
            return 0
        move_num = 0
        if self.move_counter % 2 == 0:
            for position, piece in self.white_position.items():
                if piece != 0:
                    # game_copy = self.copy()
                    available_moves = self.available_move(position)
                    for move in available_moves:
                        move_num += 1
                        game_copy = self.copy()
                        game_copy.make_move(position, move)
                        # game_copy.move_piece(position, move)
                        check = game_copy.in_check()
                        if check:
                            if game_copy.is_checkmate(check):
                                continue
                        move_num += game_copy.generate_position(max_depth, depth + 1)
        else:
            for position, piece in self.black_position.items():
                if piece != 0:
                    # game_copy = self.copy()
                    available_moves = self.available_move(position)
                    for move in available_moves:
                        move_num += 1
                        game_copy = self.copy()

                        game_copy.make_move(position, move)
                        # game_copy.move_piece(position, move)
                        check = game_copy.in_check()
                        if check:
                            if game_copy.is_checkmate(check):
                                continue
                        move_num += game_copy.generate_position(max_depth, depth + 1)
        return move_num

    def evalFunction(self):
        score = 0
        for piece in self.white_position.values():
            score += piece_value[piece]
            print(score)
        for piece in self.black_position.values():
            score -= piece_value[piece]
        return score

    def minimax(self, max_depth, depth):
        if depth > max_depth:
            return self.evalFunction()
        if self.move_counter % 2 == 0:
            scores = []
            for position, piece in self.white_position.items():
                if piece != 0:
                    # game_copy = self.copy()
                    available_moves = self.available_move(position)
                    for move in available_moves:
                        game_copy = self.copy()
                        game_copy.make_move(position, move)
                        # game_copy.move_piece(position, move)
                        check = game_copy.in_check()
                        if check:
                            if game_copy.is_checkmate(check):
                                continue
                        scores.append(game_copy.minimax(max_depth, depth + 1))
            return max(scores)
        else:
            scores = []
            for position, piece in self.black_position.items():
                if piece != 0:
                    # game_copy = self.copy()
                    available_moves = self.available_move(position)
                    for move in available_moves:
                        game_copy = self.copy()

                        game_copy.make_move(position, move)
                        # game_copy.move_piece(position, move)
                        check = game_copy.in_check()
                        if check:
                            if game_copy.is_checkmate(check):
                                continue
                        scores.append(game_copy.minimax(max_depth, depth + 1))
            return min(scores)

def main():
    color_dict = {0: 'White', 1: 'Black'}
    # game starting position
    # white_position = {i * 10 + j: 0 for i in range(1, 9) for j in range(1, 9)}
    # white_position.update({
    #     51: 1, 41: 2, 11: 3, 81: 3, 31: 4, 61: 4, 21: 5, 71: 5,
    #     12: 6, 22: 6, 32: 6, 42: 6, 52: 6, 62: 6, 72: 6, 82: 6
    # })
    # black_position = {i * 10 + j: 0 for i in range(1, 9) for j in range(1, 9)}
    # black_position.update({
    #     58: 1, 48: 2, 18: 3, 88: 3, 38: 4, 68: 4, 28: 5, 78: 5,
    #     17: 6, 27: 6, 37: 6, 47: 6, 57: 6, 67: 6, 77: 6, 87: 6
    # })

    white_position = {
        51: 1, 41: 2, 11: 3, 81: 3, 31: 4, 61: 4, 21: 5, 71: 5,
        12: 6, 22: 6, 32: 6, 42: 6, 52: 6, 62: 6, 72: 6, 82: 6
    }
    black_position = {
        58: 1, 48: 2, 18: 3, 88: 3, 38: 4, 68: 4, 28: 5, 78: 5,
        17: 6, 27: 6, 37: 6, 47: 6, 57: 6, 67: 6, 77: 6, 87: 6
    }

    board = Board(white_position, black_position)
    display_board()
    board.display_pieces()
    pygame.display.flip()

    selected_position = None
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
                if board.check_select(click_position):
                    selected_position = click_position
                    available_moves = board.available_move(click_position)
                    board.draw_available_moves(available_moves)
                else:
                    if selected_position is not None:
                        for move in available_moves:
                            if click_position == move % 100:
                                board.move_piece(selected_position, move)
                                selected_position = None
                        check = board.in_check()
                # check for mate
                if check:
                    if board.is_checkmate(check):
                        font = pygame.font.Font(None, 36)
                        text_surface = font.render(f"Checkmate! {color_dict[board.move_counter % 2]} Lost",
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

if __name__ == '__main__':
    # start = timer()
    # white_position = {
    #     51: 1, 41: 2, 11: 3, 81: 3, 31: 4, 61: 4, 21: 5, 71: 5,
    #     12: 6, 22: 6, 32: 6, 42: 6, 52: 6, 62: 6, 72: 6, 82: 6
    # }
    # black_position = {
    #     58: 1, 48: 2, 18: 3, 88: 3, 38: 4, 68: 4, 28: 5, 78: 5,
    #     17: 6, 27: 6, 37: 6, 47: 6, 57: 6, 67: 6, 77: 6, 87: 6
    # }
    # board = Board(white_position, black_position)
    # # print(board.minimax(3, 1))
    # print(board.generate_position(4, 1))
    # print(timer() - start)
    # pygame.quit()
    # sys.exit()
    main()