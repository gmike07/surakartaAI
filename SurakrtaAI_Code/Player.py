import numpy as np
from ast import literal_eval as make_tuple
from abc import ABC, abstractmethod
from Board import Action
from Enums import Tile
from Heuristics import switch_color
import random


class Player(ABC):
    def __init__(self):
        self.color = Tile.EMPTY

    @abstractmethod
    def get_action(self, board) -> Action:
        """
        :param board: gets a board object
        :return: the chosen action by the player for the given board
        """
        pass

    def get_color(self) -> Tile:
        """
        :return: the color of the player
        """
        return self.color

    def set_color(self, color: Tile):
        """
        :param color: the color wanted
        sets the color of the player
        """
        self.color = color


class HumanPlayer(Player):
    def __init__(self, is_gui=False):
        """
        :param is_gui: a boolean value is the game run with gui or not
        """
        super().__init__()
        self.is_gui = is_gui
        self.moves, self.action, self.start_point = None, None, None

    def get_action(self, board) -> Action:
        """
        :param board: gets a board object
        :return: the chosen action by the player for the given board
        """
        if self.is_gui:
            action = self.action
            self.start_point = None
            self.moves = None
            self.action = None
        else:
            points = input(('Black' if self.color == Tile.BLACK else 'Red')
                           + ' player\'s turn: <sy,sx ey,ex>\n').split()
            action = Action(self.color, make_tuple(points[0]), make_tuple(points[1]))
        return action

    def update_info_point_chosen(self, board, y, x):
        """
        :param board: a board object
        :param y: the current y position of the cursor
        :param x: the current x position of the cursor
        updates the variables of the chosen piece and returns a set of legal
        move with the chosen piece
        """
        self.start_point = (y, x)
        self.moves = {action for action in board.get_legal_actions(self.color)
                      if action.get_start_point() == (y, x)}
        if len(self.moves) == 0:
            self.start_point = None
            self.action = None
        return self.moves

    def update_move(self, game, y, x):
        """
        :param game: a game object
        :param y: the current y position of the cursor
        :param x: the current x position of the cursor
        :return: True iff the player has selected a move, a set of legal moves
                 if the set is not empty and a move was chose, else False
        this function updates the human player's decision, which tile is chosen
        """
        board = game.get_board()
        if not self.is_gui or not board.is_legal_index(y, x):
            return False
        if board.get_np_board()[y, x] != self.color and self.start_point is None:
            return False
        if self.moves is None:
            # the chosen piece is start_point
            return self.update_info_point_chosen(board, y, x)
        else:
            action = Action(self.color, self.start_point, (y, x))
            if Action(self.color, self.start_point, (y, x)) in self.moves:
                self.action = action
                return True
            # the chosen piece is the new start_point
            return self.update_info_point_chosen(board, y, x)


class MiniMaxPlayer(Player):
    def __init__(self, depth, heuristic):
        """
        :param depth: the depth of the tree
        :param heuristic: the heuristic for evaluation
        """
        super().__init__()
        self.depth = depth
        self.heuristic = heuristic

    def get_action(self, board) -> Action:
        """
        :param board: gets a board object
        :return: the chosen action by the player for the given board
        """
        action, score = self.minimax_alpha_beta(board, self.depth, self.color)
        return action

    def minimax_alpha_beta(self, game_state, depth, color, is_max=True,
                           alpha=-float('inf'), beta=float('inf')):
        """
        :param game_state: the current game state
        :param depth: the depth left
        :param color: the current color of the player
        :param is_max: boolean if the player is the max player or not
        :param alpha: the alpha parameter
        :param beta: the beta parameter
        :return: a tuple of (Action, score) for the best action for the player
        """
        actions = game_state.get_legal_actions(color)
        if depth == 0 or len(actions) == 0:
            return None, self.heuristic(game_state, self.color)
        if is_max:
            max_action = None
            for action in actions:
                state = game_state.__copy__()
                state.do_action(action)
                last_action, score = self.minimax_alpha_beta(state, depth - 1,
                                                             switch_color(color),
                                                             False, alpha, beta)
                if alpha < score:
                    max_action, alpha = action, score
                if alpha >= beta:
                    return None, alpha
            return max_action, alpha
        else:
            min_action = None
            for action in actions:
                state = game_state.__copy__()
                state.do_action(action)
                last_action, score = self.minimax_alpha_beta(state, depth - 1,
                                                             switch_color(color),
                                                             True, alpha, beta)
                if beta > score:
                    min_action, beta = action, score
                if alpha >= beta:
                    return None, beta
            return min_action, beta


class Node:
    total_simulations = 0

    def __init__(self, state, color, prev=None, action=None):
        """
        :param state: the current state of the game
        :param color: the color of the node
        :param prev: a pointer to the previous node or None
        :param action: the action that created this Node or None
        """
        self.state = state
        self.color = color
        self.next = set()
        self.prev = prev
        self.action = action
        self.visit_num = 0
        self.win = 0

    def expand(self, add_actions=False):
        """
        :param add_actions: boolean if should remember the actions to create the nodes
        creates all the children of the node
        """
        actions = self.state.get_legal_actions(self.color)
        for action in actions:
            next_state = self.state.__copy__()
            next_state.do_action(action)
            self.next.add(Node(next_state, switch_color(self.color),
                               self, action if add_actions else None))

    def get_uct(self):
        """
        :return: get the value of the node
        """
        return (self.win / self.visit_num + (2 * np.log(Node.total_simulations) / self.visit_num) ** 0.5) \
            if self.visit_num else float('inf')

    @staticmethod
    def best_child_uct(node):
        """
        :param node: the node
        :return: the best child of the node (unexplored is always better)
        """
        return max(node.next, key=lambda n: n.get_uct())


class MonteCarloPlayer(Player):
    def __init__(self, depth, num, heuristic):
        """
        :param depth: the depth of the rollout each time
        :param num: the number of iteration
        :param heuristic: the heuristic for evaluation
        """
        super().__init__()
        self.depth = depth
        self.num = num
        self.heuristic = heuristic

    def get_action(self, board) -> Action:
        """
        :param board: gets a board object
        :return: the chosen action by the player for the given board
        """
        root = Node(board, self.color)
        for i in range(self.num):
            leaf = self.traverse(root)
            leaf.expand(leaf == root)
            result = self.rollout(leaf)
            self.backpropagate(leaf, result)
            Node.total_simulations += 1
        best = max(root.next, key=lambda n: n.win / n.visit_num if n.visit_num else -float('inf'))
        return best.action

    @staticmethod
    def traverse(node):
        """
        :param node: gets the root
        :return: an unexplored child of the root that has the most potential
        """
        while node.next and node.get_uct() != float('inf'):
            node = Node.best_child_uct(node)
        return node

    def rollout(self, node):
        """
        :param node: the node to simulate through
        simulates a run from node for depth steps
        """
        state = node.state.__copy__()
        cur_color = node.color
        for _ in range(self.depth):
            actions = state.get_legal_actions(cur_color)
            if len(actions) == 0:
                return self.heuristic(state, self.color)
            state.do_action(random.choice(tuple(actions)))
            cur_color = switch_color(cur_color)
        return self.heuristic(state, self.color)

    def backpropagate(self, node, result):
        """
        :param node: the current node
        :param result: the result by the simulation
        updates the node with the result and calls to update the previous one
        """
        if node:
            node.visit_num += 1
            node.win += result
            self.backpropagate(node.prev, result)


class RandomPlayer(Player):
    def __init__(self, seed=42):
        super().__init__()
        random.seed(seed)

    def get_action(self, board) -> Action:
        """
        :param board: gets a board object
        :return: the chosen action by the player for the given board
        """
        return random.choice(tuple(board.get_legal_actions(self.color)))
