#   ### ##    ##         ##     ## ###   #### #### #### #### #### #### ####
#  ##    ##  ##           ##   ##    ##  #### #### #### #### #### #### ####
# ##      ####             ## ##      ## #### #### #### #### #### #### ####
# ##       ##    ####       ###       ##  ##   ##   ##   ##   ##   ##   ##
# ##       ##    ####      ## ##      ##
#  ##      ##     ##      ##   ##    ##  #### #### #### #### #### #### ####
#   ###    ##    ##      ##     ## ###   #### #### #### #### #### #### ####

import numpy as np
from itertools import cycle
from Enums import Tile, LoopDirection

HEIGHT = 6
WIDTH = 6


class Action:  # always legal
    def __init__(self, color, point1, point2):
        """
        :param color: the color of the current action
        :param point1: the point of the tile that we want to move
        :param point2: the point to where we want to move the tile to
        """
        self.color = color
        self.start_point = point1
        self.end_point = point2

    def __eq__(self, other):
        return self.color == other.color and \
               self.start_point == other.start_point and \
               self.end_point == other.end_point

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return repr(self.color) + ' ' + str(self.start_point) + ' ' + str(
            self.end_point)

    def get_color(self):
        """
        :return: the color of the player doing the action
        """
        return self.color

    def get_start_point(self):
        """
        :return: the start point of the action (i.e. the tile to move)
        """
        return self.start_point

    def get_end_point(self):
        """
        :return: the end point of the action (i.e. where to move the tile to)
        """
        return self.end_point


class Board:  # turns out to be Board

    def init_portal_dict(self):
        """
        :return: this function creates a dictionary of (y,x) --> (y_new, x_new)
                 which corresponds to the loops out of bounds in the game
        """
        mapping = {}
        # top half
        for y in range(1, self.height // 2):
            # first quarter (left)
            mapping[(y, 0)] = (0, y)
            mapping[(0, y)] = (y, 0)
            # second quarter (right)
            mapping[(y, self.width - 1)] = (0, self.width - 1 - y)
            mapping[(0, self.width - 1 - y)] = (y, self.width - 1)
        # bottom half
        for y in range(self.height - 2,
                       self.height // 2 - 1 * (not self.height % 2), -1):
            # third quarter (left)
            mapping[(y, 0)] = (self.height - 1, self.width - 1 - y)
            mapping[(self.height - 1, self.width - 1 - y)] = (y, 0)
            # fourth quarter (right)
            mapping[(self.height - 1, y)] = (y, self.width - 1)
            mapping[(y, self.width - 1)] = (self.height - 1, y)

        return mapping

    def __init__(self, height=HEIGHT, width=WIDTH):
        """
        creates the board and initializes the portal dict to hold the loops around
        :param height: gets the height of the board
        :param width: gets the width of the board
        """
        self.height, self.width = height, width
        self.board = np.zeros((self.height, self.width), dtype=Tile)
        self.board[self.board == 0] = Tile.EMPTY
        self.board[:(self.height // 2 - 1), :] = Tile.BLACK
        self.board[-(self.height // 2 - 1):, :] = Tile.RED
        self.portal_dict = self.init_portal_dict()
        self.red_count = np.sum(self.board == Tile.RED)
        self.black_count = np.sum(self.board == Tile.BLACK)
        self.last_eat_red = 0
        self.last_eat_black = 0

    def is_legal_index(self, y: int, x: int) -> bool:
        """
        :param y: gets the y in the board
        :param x: gets the x in the board
        :return: returns true if the (y,x) is a valid entry in the board
        """
        return 0 <= y < self.height and 0 <= x < self.width

    def _check_tile(self, y: int, x: int, tile: Tile) -> bool:
        """
        :param y: gets the y in the board
        :param x: gets the x in the board
        :param tile: the tile type
        :return: true iff (y,x) valid index and
                 board[y,x] contains tile of type input tile
        """
        return self.is_legal_index(y, x) and self.board[y, x] == tile

    def _get_king_actions(self, y: int, x: int, player: Tile) -> set:
        """
        :param y: the y of the tile we want to find the actions where we can move it to
        :param x: the x of the tile we want to find the actions where we can move it to
        :param player: the color of the player making the move
        :return: the legal king actions from position (y,x) for player player
        """
        king_actions = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self._check_tile(y + j, x + i, Tile.EMPTY):
                    king_actions.add(Action(player, (y, x), (y + j, x + i)))
        return king_actions

    def portal(self, y: int, x: int) -> (int, int, LoopDirection):
        """
        :param y: the current y
        :param x: the current x
        :return: a tuple (y, x, direction) representing the next part of the loop
        """
        y, x = self.portal_dict[(y, x)]
        if y == 0:
            return y, x, LoopDirection.DOWN
        elif y == self.height - 1:
            return y, x, LoopDirection.UP
        elif x == 0:
            return y, x, LoopDirection.RIGHT
        return y, x, LoopDirection.LEFT

    def _get_loop_action(self, y, x, direction, player):
        """
        :param y: the current y
        :param x: the current x
        :param direction: the direction we loop through
        :param player: the color of the player
        :return: the enemy found in that direction on None
                 if we didn't encounter an enemy
        """
        for loop_count in range(5):  # portals
            # run to the next portal / another piece
            y_dir, x_dir = direction.value
            while self._check_tile(y, x, Tile.EMPTY):
                y, x = y + y_dir, x + x_dir
            #
            if not self.is_legal_index(y, x) and (y - y_dir, x - x_dir) in self.portal_dict:
                y, x, direction = self.portal(y - y_dir, x - x_dir)
            # we reached a player without going through a portal or it
            # is our player so we can't eat it
            elif loop_count == 0 or self.board[y, x] == player:
                return None
            # we reached the enemy player so we can eat it
            else:
                return y, x
        return None

    def _get_loop_actions(self, y, x, directions, player):
        """
        :param y: the current y
        :param x: the current x
        :param directions: the directions we search in
        :param player: the player to search actions for
        :return: all the loop move actions that can be preformed by player
                 from points (y, x) via the given directions
        """
        temp, self.board[y, x] = self.board[y, x], Tile.EMPTY
        locs = set()
        for direction in directions:
            val = self._get_loop_action(y, x, direction, player)
            if val is not None and val not in locs:
                locs.add(Action(player, (y, x), val))
        self.board[y, x] = temp
        return locs

    def get_legal_actions(self, player: Tile):
        """
        :param player: the color of the player to check
        :return: all the legal actions to the player as a set
        """
        ys, xs = np.where(self.board == player)
        legal_actions = set()
        # get free not eating move
        for y, x in zip(ys, xs):
            legal_actions.update(self._get_king_actions(y, x, player))
        # calculate eating move
        directions = [LoopDirection.UP, LoopDirection.DOWN,
                      LoopDirection.LEFT, LoopDirection.RIGHT]
        for y, x in zip(ys, xs):
            legal_actions.update(self._get_loop_actions(y, x, directions, player))
        return legal_actions

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        return self.board == other.board

    def __copy__(self):
        copy_board = Board(0, 0)
        copy_board.height, copy_board.width = self.height, self.width
        copy_board.board = np.copy(self.board)
        copy_board.portal_dict = self.portal_dict
        copy_board.red_count = self.red_count
        copy_board.black_count = self.black_count
        copy_board.last_eat_black = self.last_eat_black
        copy_board.last_eat_red = self.last_eat_red
        return copy_board

    def is_legal_action(self, action: Action) -> bool:
        """
        :param action: gets an action
        :return: true iff the action is legal in the current board
        """
        return action in self.get_legal_actions(action.get_color())

    def do_action(self, action: Action):
        """
        :param action: gets a legal action
        preforms the action on the current board
        """
        if action.color == Tile.RED:
            self.last_eat_red += 1
        else:
            self.last_eat_black += 1
        if self.board[action.end_point] == Tile.RED:
            self.red_count -= 1
            self.last_eat_black = 0
        if self.board[action.end_point] == Tile.BLACK:
            self.black_count -= 1
            self.last_eat_red = 0
        self.board[action.end_point] = self.board[action.start_point]
        self.board[action.start_point] = Tile.EMPTY

    def print_board(self):  # textual. WITHOUT loops
        """
        prints the board to the terminal
        """
        for i in range(len(self.board)):
            print(f'[{i}]', self.board[i])
        print('   ', np.arange(WIDTH))

    def get_num_pieces(self, color: Tile):
        """
        :param color: the color
        :return: the number of pieces in the board of the given color
        """
        return self.red_count if color == Tile.RED else self.black_count

    def get_np_board(self):
        """
        :return: returns the board as a numpy array
        """
        return self.board

    def get_pieces_positions(self, color: Tile):
        """
        :param color: the color interested
        :return: a set of (y,x) for all positions in the board with the given color
        """
        ys, xs = np.where(self.board == color)
        return set((y, x) for y, x in zip(ys, xs))

    def revert_action(self, action: Action, changed_tile: Tile):
        """
        :param action: the action to revert
        :param changed_tile: the tile that was eaten by the action
        the function reverts the last action preformed
        """
        self.board[action.get_start_point()] = action.get_color()
        self.board[action.get_end_point()] = changed_tile

    def get_last_eating_move_red(self) -> int:
        """
        :return: the number of moves since the red ate
        """
        return self.last_eat_red

    def get_last_eating_move_black(self) -> int:
        """
        :return: the number of moves since the black ate
        """
        return self.last_eat_black


class Surakarta:  # Game
    def __init__(self, black_player, red_player, height=HEIGHT, width=WIDTH):
        """
        :param black_player: an object of black player
        :param red_player: an object of red player
        :param height: the height of the board
        :param width: the width of the board
        """
        # players are (currently) Player.HUMAN/Player.AI
        self.black_player = black_player
        self.black_player.set_color(Tile.BLACK)
        self.red_player = red_player
        self.red_player.set_color(Tile.RED)
        self.cur_player_iter = cycle([self.red_player, self.black_player])
        self.cur_player = next(self.cur_player_iter)
        # self.cur_player = Tile.BLACK
        self.board = Board(height, width)
        self.legal_moves = self.board.get_legal_actions(self.cur_player.get_color())

    def move(self) -> bool:
        """
        tries to do one move and returns true iff the current move was legal
        """
        action = self.cur_player.get_action(self.board)
        if action not in self.legal_moves or \
                action.get_color() != self.cur_player.get_color():
            return False
        self.board.do_action(action)
        self.cur_player = next(self.cur_player_iter)
        self.legal_moves = self.board.get_legal_actions(self.cur_player.get_color())
        return True

    def print_board(self):
        """
        :return: prints the current board to the terminal
        """
        self.board.print_board()

    def is_endgame(self) -> bool:
        """
        :return: true iff the game has ended
        """
        last_eat_red = self.board.get_last_eating_move_red()
        last_eat_black = self.board.get_last_eating_move_black()
        return self.board.get_num_pieces(self.cur_player) == 0 or \
               (type(self.legal_moves) == set and len(self.legal_moves) == 0) or \
               min(last_eat_black, last_eat_red) >= 40

    def get_board(self) -> Board:
        """
        :return: the board object that represents the current state in the game
         """
        return self.board

    def get_current_player(self):
        """
        :return: a player object of the current player
        """
        return self.cur_player

    def get_winner(self) -> str:
        """
        :return: a string of the winning player and a tie if it was a
                 tie, and if the game is not over return the empty string,
                 called after the game has ended
        """
        if not self.is_endgame():
            return ''
        if self.board.get_num_pieces(Tile.RED) < \
                self.board.get_num_pieces(Tile.BLACK):
            return 'Black'
        if self.board.get_num_pieces(Tile.RED) > \
                self.board.get_num_pieces(Tile.BLACK):
            return 'Red'
        return 'Tie'
