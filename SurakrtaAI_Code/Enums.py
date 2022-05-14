from enum import Enum


class Tile(Enum):
    EMPTY = 0
    BLACK = 1
    RED = 2
    HINT = 3

    def __repr__(self):
        if self == Tile.BLACK:
            return "B"
        if self == Tile.RED:
            return "R"
        return " "


class LoopDirection(Enum):
    DOWN = (1, 0)
    UP = (-1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
