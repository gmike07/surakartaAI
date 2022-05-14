import numpy as np
from Board import HEIGHT, WIDTH

# screen & board dimensions
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 680
SCREEN_CENTER = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50
BOARD_SIZE = 300
BLOCK_SIZE = BOARD_SIZE // 5
# borders
MIN_X = SCREEN_CENTER[0] - (BOARD_SIZE // 2)
MIN_Y = SCREEN_CENTER[1] - (BOARD_SIZE // 2)
MAX_X = MIN_X + (WIDTH - 1) * BLOCK_SIZE
MAX_Y = MIN_Y + (HEIGHT - 1) * BLOCK_SIZE

BOARD_LEFT_TOP = np.array([MIN_X, MIN_Y])
BOARD_LEFT_BOTTOM = np.array([MIN_X, MAX_Y])
BOARD_RIGHT_TOP = np.array([MAX_X, MIN_Y])
BOARD_RIGHT_BOTTOM = np.array([MAX_X, MAX_Y])
# colors
BLACK_COLOR = 0, 0, 0
BACKGROUND_COLOR = tuple(np.random.randint(0, 255, 3))
GRID = tuple(np.random.randint(0, 255, 3))
WHITE_COLOR = 255, 255, 255
