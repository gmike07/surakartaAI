#   ### ##     ##         ##    ## ###   #### #### #### #### #### #### ####
#  ##    ##   ##           ##  ##    ##  #### #### #### #### #### #### ####
# ##      ## ##             ####      ## #### #### #### #### #### #### ####
# ##       ###    ####       ##       ##  ##   ##   ##   ##   ##   ##   ##
# ##      ## ##   ####       ##       ##
#  ##    ##   ##   ##        ##      ##  #### #### #### #### #### #### ####
#   ### ##     ## ##         ##    ###   #### #### #### #### #### #### ####

import pygame
import sys
import os
import time
from Board import Surakarta
from Player import HumanPlayer
from GUIConstants import *
from Enums import Tile
print(BACKGROUND_COLOR, GRID)


def calculate_loop_rect(rect_size, rect_offset):
    """
    :param rect_size: gets the rect size
    :param rect_offset: gets the rect offset
    :return: all the rects that are created for drawing the loops
    """
    points = [BOARD_LEFT_TOP, BOARD_RIGHT_TOP, BOARD_RIGHT_BOTTOM, BOARD_LEFT_BOTTOM]
    return [pygame.Rect(point[0] - rect_offset, point[1] - rect_offset, rect_size, rect_size)
            for point in points]


class GUI:
    def __init__(self, game):
        """
        :param game: gets a Surakarta game object
        """
        self.game = game
        pygame.init()
        font = pygame.font.SysFont('constantia', 72)
        sub_font = pygame.font.SysFont('constantia', 36)
        self.title = font.render('Surakarta', True, GRID)
        self.turn_subtitle = sub_font.render('Turn: ', True, GRID)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background_img = pygame.image.load('background.jpg')
        self.red_piece_img = pygame.image.load('Red.png')
        self.black_piece_img = pygame.image.load('Black.png')
        self.legal_dest_img = pygame.image.load('Green.png')
        self.legal_dest_img.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.title,
                         (SCREEN_WIDTH // 2 - self.title.get_width() // 2,
                          SCREEN_HEIGHT >> 5))
        self.screen.blit(self.turn_subtitle,
                         (SCREEN_WIDTH // 12 - self.turn_subtitle.get_width() // 2 + 10, SCREEN_HEIGHT >> 4))

    @staticmethod
    def click_in_range(x, y):
        """
        :param x: the current x value
        :param y: the current y value
        :return: true iff x and y are the board's range
        """
        return MIN_X - 0.5 * BLOCK_SIZE <= x <= MAX_X + 0.5 * BLOCK_SIZE \
               and MIN_Y - 0.5 * BLOCK_SIZE <= y <= MAX_Y + 0.5 * BLOCK_SIZE

    def get_mouse_position(self):
        """
        :return: the coordinates the the mouse in the board as (y, x),
                 if it is invalid return (None, None)
        """
        x, y = pygame.mouse.get_pos()
        if not self.click_in_range(x, y):
            return None, None
        new_x = int((x - MIN_X + 0.5 * BLOCK_SIZE) * WIDTH / (MAX_X - MIN_X + BLOCK_SIZE))
        new_y = int((y - MIN_Y + 0.5 * BLOCK_SIZE) * HEIGHT / (MAX_Y - MIN_Y + BLOCK_SIZE))
        return new_y, new_x

    def draw_screen(self, moves, MAX_PIECES=12):
        """
        :param moves: a set of the hint moves for the human player
        :param MAX_PIECES: the max amount of pieces allowed in the board for each color
        draws the screen for the user.
        """
        self.screen.blit(self.static_surface, (0, 0))
        self.draw_pieces()
        self.draw_piece(-3, -3, self.game.get_current_player().get_color())
        red_dead = MAX_PIECES - self.game.get_board().get_num_pieces(Tile.RED)
        black_dead = MAX_PIECES - self.game.get_board().get_num_pieces(Tile.BLACK)
        for i in range(red_dead):
            self.draw_piece(6.5 - (i // 2), -5 + (i % 2), Tile.RED)
        for i in range(black_dead):
            self.draw_piece(6.5 - (i // 2), 10 - (i % 2), Tile.BLACK)
        for action in moves:
            new_y, new_x = action.get_end_point()
            self.draw_piece(new_y, new_x, Tile.HINT)
        pygame.display.flip()

    def handle_human_player_action(self) -> bool:
        """
        :return: True iff the human player chose his move
        """
        y, x = self.get_mouse_position()
        if y is None or not self.game.get_board().is_legal_index(y, x):
            return False
        if not isinstance(self.game.get_current_player(), HumanPlayer):
            return False
        # a bit of changes
        moves = self.game.get_current_player().update_move(self.game, y, x)
        if type(moves) == bool:
            return moves
        self.draw_screen(moves)
        return False

    def endgame(self):
        """
        this function handles the end game, prints the winner and stops the game
        """
        winner = self.game.get_winner()
        sub_font = pygame.font.SysFont('constantia', 36)
        winner_text = sub_font.render(f'{winner} Wins!' if winner != 'Tie'
                                      else 'It\'s a tie!', True, GRID)
        self.screen.blit(winner_text, (21 * SCREEN_WIDTH // 24 - winner_text.get_width() // 2 + 10,
                                       SCREEN_HEIGHT >> 4))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

    def run(self):
        """
        runs the game via the GUI
        """
        self.draw_board()
        self.static_surface = pygame.display.get_surface().copy()
        self.draw_screen(set())

        while not self.game.is_endgame():
            human_player_decided = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    human_player_decided = self.handle_human_player_action()
            if not isinstance(self.game.get_current_player(), HumanPlayer) \
                    or human_player_decided:
                self.game.move()
                self.draw_screen(set())
                # time.sleep(0.2)
        # Thanos be ready
        self.endgame()

    def draw_board(self):
        """
        draw the board to the screen
        """
        for y in range(HEIGHT):
            (MIN_X, MIN_Y + y * BLOCK_SIZE)
            pygame.draw.line(self.screen, GRID, (MIN_X, MIN_Y + y * BLOCK_SIZE),
                             (MAX_X, MIN_Y + y * BLOCK_SIZE), 2)
        for x in range(WIDTH):
            pygame.draw.line(self.screen, GRID, (MIN_X + x * BLOCK_SIZE, MIN_Y),
                             (MIN_X + x * BLOCK_SIZE, MAX_Y), 2)
        angle = 0
        # draw outer loops
        for loop_rect in calculate_loop_rect(4 * BLOCK_SIZE, 2 * BLOCK_SIZE):
            pygame.draw.arc(self.screen, GRID, loop_rect, angle,
                            angle + 1.5 * np.pi, 2)
            angle += 1.5 * np.pi
        # draw inner loops
        for loop_rect in calculate_loop_rect(2 * BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.arc(self.screen, GRID, loop_rect, angle,
                            angle + 1.5 * np.pi, 2)
            angle += 1.5 * np.pi

    def draw_piece(self, y, x, color):
        """
        :param y: the y of the piece to draw
        :param x: the x of the piece to draw
        :param color: the color of the piece to draw
        draws the piece in the given location to the screen
        """
        if color == Tile.RED:
            img_rect = self.red_piece_img.get_rect()
            img_rect.center = MIN_X + x * BLOCK_SIZE, MIN_Y + y * BLOCK_SIZE
            self.screen.blit(self.red_piece_img, img_rect)
        elif color == Tile.BLACK:
            img_rect = self.black_piece_img.get_rect()
            img_rect.center = MIN_X + x * BLOCK_SIZE, MIN_Y + y * BLOCK_SIZE
            self.screen.blit(self.black_piece_img, img_rect)
        if color == Tile.HINT:
            img_rect = self.legal_dest_img.get_rect()
            img_rect.center = MIN_X + x * BLOCK_SIZE, MIN_Y + y * BLOCK_SIZE
            self.screen.blit(self.legal_dest_img, img_rect)

    def draw_pieces(self):
        """
        draws all pieces to the screen
        """
        for row in range(HEIGHT):
            for col in range(WIDTH):
                self.draw_piece(row, col, self.game.board.board[row, col])


# via terminal
class NotGUI:
    def __init__(self, game):
        """
        :param game: gets a Surakarta game object
        """
        self.game = game

    def print_board(self):  # textual. WITHOUT loops
        """
        prints the board in the terminal
        """
        self.game.print_board()

    def run(self):
        """
        runs the game via the terminal
        """
        while not self.game.is_endgame():
            self.game.board.print_board()
            if self.game.move() is False:
                print("Illegal move")
            else:
                time.sleep(1)
                os.system('cls||clear')
        winner = self.game.get_winner()
        print(f'{winner} Wins!' if winner != 'Tie' else 'It\'s a tie!')