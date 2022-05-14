from Enums import Tile
from Board import Board
import numpy as np

position_array = np.array([[0, 5, 5, 5, 5, 0],
                           [5, 10, 20, 20, 10, 5],
                           [5, 20, 10, 10, 20, 5],
                           [5, 20, 10, 10, 20, 5],
                           [5, 10, 20, 20, 10, 5],
                           [0, 5, 5, 5, 5, 0]])

position_array_2 = np.array([[0, 5, 5, 5, 5, 0],
                             [5, 20, 10, 10, 20, 5],
                             [5, 10, 20, 20, 10, 5],
                             [5, 10, 20, 20, 10, 5],
                             [5, 20, 10, 10, 20, 5],
                             [0, 5, 5, 5, 5, 0]])


def switch_color(color: Tile):
    """
    :param color: the given color
    :return: the opposite color
    """
    return Tile.BLACK if color == Tile.RED else Tile.RED


def basic_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that combines attack and defense to evaluate the board
    """
    return board.get_num_pieces(player_color) - \
           board.get_num_pieces(switch_color(player_color))


def position_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that combines evaluate the board via the position of the
    pieces
    """
    return np.sum(position_array * (board.get_np_board() == player_color))


def position2_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that combines evaluate the board via the position of the
    pieces, another evaluator
    """
    return np.sum(position_array_2 * (board.get_np_board() == player_color))


def attack_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that evaluates the board via how many has the player eaten
    """
    return -board.get_num_pieces(switch_color(player_color))


def defensive_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that evaluates the board via how many pieces the
    player has left
    """
    return board.get_num_pieces(player_color)


def smart_heuristic(board: Board, player_color: Tile):
    """
    :param board: the board object
    :param player_color: the given color
    :return: a number that combines position, attack and defense to evaluate
    the board
     """
    return position_heuristic(board, player_color) * 0.1 + \
           attack_heuristic(board, player_color) + \
           defensive_heuristic(board, player_color)
