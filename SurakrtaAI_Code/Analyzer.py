from Board import Surakarta
import numpy as np
from tqdm import tqdm
from Enums import Tile
from Heuristics import basic_heuristic, smart_heuristic, switch_color
from Player import MiniMaxPlayer, MonteCarloPlayer, RandomPlayer
import time
import pandas as pd
from pandas import ExcelWriter


"""
Graphs:
1. reaction_time(agent)
2. win_percentage(agent vs. all)
3. 
"""


class Analyzer:
    def __init__(self, black_player, red_player, number_of_games=20):
        """
        :param black_player: get the black player
        :param red_player: get the red player
        :param number_of_games: get the number of games
        """
        self.number_of_games = number_of_games
        self.black_player = black_player
        self.red_player = red_player
        self.red_surviving_tiles = np.zeros(number_of_games)
        self.black_surviving_tiles = np.zeros(number_of_games)
        self.game_iteration = 0
        self.black_time = []
        self.red_time = []

    def simulate_run(self):
        """
        run a simulation and store the results
        """
        game = Surakarta(self.black_player, self.red_player)
        while not game.is_endgame():
            current_color = game.get_current_player().get_color()
            current_time1 = time.time()
            game.move()
            current_time2 = time.time()
            if current_color == Tile.RED:
                self.red_time.append(current_time2 - current_time1)
            else:
                self.black_time.append(current_time2 - current_time1)
        board = game.get_board()
        i = self.game_iteration
        self.red_surviving_tiles[i] = board.get_num_pieces(Tile.RED)
        # print(board.print_board())
        self.black_surviving_tiles[i] = board.get_num_pieces(Tile.BLACK)
        self.game_iteration += 1

    def simulate(self):
        """
        do a lot of simulations and store the results
        """
        for _ in tqdm(range(self.number_of_games)):
            self.simulate_run()

    def get_mean_time_per_move(self, color):
        """
        :param color: the color data interested
        :return: the avg time it took to make a move
        """
        if color == Tile.RED:
            return np.mean(self.red_time)
        return np.mean(self.black_time)

    def get_win_precentage(self, color):
        """
        :param color: the color data interested
        :return: the avg win %
        """
        if color == Tile.RED:
            return np.mean(self.red_surviving_tiles > self.black_surviving_tiles)
        return np.mean(self.red_surviving_tiles < self.black_surviving_tiles)

    def get_score_precentage(self, color):
        """
        :param color: the color data interested
        :return: the avg score %
        """
        if color == Tile.RED:
            return (12 - np.mean(self.black_surviving_tiles)) / 12
        return (12 - np.mean(self.red_surviving_tiles)) / 12


HEURISTICS = [basic_heuristic, smart_heuristic]
PLAYERS = [MiniMaxPlayer(depth, heuristic)
           for depth in range(1, 6) for heuristic in HEURISTICS]
PLAYERS.extend([MonteCarloPlayer(depth, int(2 ** (depth + 1)), heuristic)
                      for depth in range(2, 15, 2) for heuristic in HEURISTICS])


def get_statistics(analyzer1, analyzer2, color, i, j):
    """
    :param analyzer1: the first analyzer of the game
    :param analyzer2: the second analyzer of the game
    :param color: the color interested
    :param i: the player
    :param j: the enemy
    :return: a df of the statistics of the player i against j
    """
    avg_time = (analyzer1.get_mean_time_per_move(color) +
                analyzer2.get_mean_time_per_move(switch_color(color))) / 2
    avg_time_enemy = (analyzer1.get_mean_time_per_move(switch_color(color)) +
                      analyzer2.get_mean_time_per_move(color)) / 2
    perc_time = avg_time / (avg_time + avg_time_enemy)
    win_percentage = (analyzer1.get_win_precentage(color) +
                      analyzer2.get_win_precentage(switch_color(color))) / 2
    score = (analyzer1.get_score_precentage(color) +
             analyzer2.get_score_precentage(switch_color(color))) / 2
    return pd.DataFrame({'avg runtime': avg_time,
                         '% score': score,
                         '% time': [perc_time],
                         '% win': win_percentage,
                         'enemy': j,
                         'player': i})


def simulations(players, file_name='', num_games=10):
    """
    :param players: gets a list of players to test
    :param file_name: the name of the file to save the simulations into
    :param num_games: gets the number of games to test on
    saves the statistics to an excel file to later use
    """
    arr = []
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1, player2 = players[i], players[j]

            analyzer1 = Analyzer(player1, player2, number_of_games=num_games // 2)
            analyzer1.simulate()

            analyzer2 = Analyzer(player2, player1, number_of_games=num_games // 2)
            analyzer2.simulate()

            arr.append(get_statistics(analyzer1, analyzer2, Tile.BLACK, i, j))
            print(arr[-1])
            arr.append(get_statistics(analyzer1, analyzer2, Tile.RED, j, i))
            print(arr[-1])
    df = pd.concat(arr)
    print(df)
    writer = ExcelWriter(f'{file_name}.xlsx')
    df.to_excel(writer, f'Sheet1')
    writer.save()

# commented because plotnine DOESN'T work on linux!!
# from plotnine import *
# def time_graph(num_games=6):
#     """
#     :param num_games: the number of games to test
#     saves the runtime of the red players to an excel file
#     """
#     dfs = []
#     for i in tqdm(range(len(PLAYERS))):
#         player = RandomPlayer(Tile.BLACK)
#         analyzer1 = Analyzer(player, PLAYERS[i], number_of_games=num_games // 2)
#         analyzer1.simulate()
#         player = RandomPlayer(Tile.BLACK)
#         analyzer2 = Analyzer(PLAYERS[i], player, number_of_games=num_games // 2)
#         analyzer2.simulate()
#         player_time = get_statistics(analyzer1, analyzer2, Tile.RED, i, 0)['avg runtime']
#         dfs.append(pd.DataFrame({'player index': [i],
#                                  'avg time': player_time,
#                                  'is minimax': isinstance(PLAYERS[i], MiniMaxPlayer),
#                                  'is smart heuristic': PLAYERS[i].heuristic == smart_heuristic}))
#         print(dfs[-1])
#     df = pd.concat(dfs)
#     print(df)
#     writer = ExcelWriter('PythonExport3.xlsx')
#     df.to_excel(writer, f'Sheet1')
#     writer.save()
#
#
# def draw_graph_monte_carlo(excel_file):
#     """
#     :param excel_file: gets an excel file
#     draws the time graph from the excel and saves it
#     """
#     df = pd.read_excel(excel_file)
#     df['depth'] = 2*(df['player index'] // 2) + 2
#     df['heuristic'] = df['is smart heuristic']
#     mask = df['heuristic'] == True
#     df['heuristic'][mask] = 'H5'
#     df['heuristic'][~mask] = 'H4'
#     df = df[:-2]
#     plot = ggplot(df) + \
#            geom_point(aes(x='depth', y='avg time', color='heuristic')) + \
#            geom_line(aes(x='depth', y='avg time', color='heuristic')) + \
#            ggtitle('Monte-Carlo time \ depth (with $2^{depth+1}$ simulations)') + \
#            labs(x='depth', y='avg time per move (sec)')
#     print(plot)
#     ggsave(plot, 'monte carlo point line.png')
#
#
# def draw_graph_minimax(excel_file):
#     """
#     :param excel_file: gets an excel file
#     draws the time graph from the excel and saves it
#     """
#     df = pd.read_excel(excel_file)
#     df['depth'] = (df['player index'] // 2) + 1
#     df['heuristic'] = df['is smart heuristic']
#     mask = df['heuristic'] == True
#     df['heuristic'].loc[mask] = 'H5'
#     df['heuristic'].loc[~mask] = 'H4'
#     plot = ggplot(df) + \
#            geom_point(aes(x='depth', y='avg time', color='heuristic')) + \
#            geom_line(aes(x='depth', y='avg time', color='heuristic')) + \
#            ggtitle('Minimax time \ depth') + \
#            labs(x='depth', y='avg time per move (sec)')
#     print(plot)
#     ggsave(plot, 'minimax point line.png')
#
#
# def measure_time_graphs():
#     """
#     measures the average run time and then draws the graphs
#     """
#     time_graph()
#     draw_graph_minimax('minimax times.xlsx')
#     draw_graph_monte_carlo('monte carlo times.xlsx')
#
#
# def draw_results():
#     """
#     use the results from the excel to draw a bar graph of the win rate and score
#     """
#     df = pd.DataFrame(
#         {
#             'agent': ['MCST(8, 512, H4)', 'MCST(8, 512, H5)', 'MINIMAX(3, H4)', 'MINIMAX(3, H5)'],
#             'win rate': [0.1, 0.666666667, 0.466666667, 0.466666667],
#             'score rate': [12*0.713888889, 12*0.719444444, 12*0.65, 12*0.6]
#         }
#     )
#     p1 = ggplot(df) + geom_bar(aes(x='agent', y = 'win rate'), stat='identity') \
#         + ggtitle("Win Rate per agent") \
#         + labs(y='win rate', x='agents')
#     p2 = ggplot(df) + geom_bar(aes(x='agent', y = 'score rate'), stat='identity') \
#         + ggtitle("Score per agent") \
#         + labs(y='average score (12 * score rate)', x='agents')
#     print(p1)
#     print(p2)
#     ggsave(p1, 'agents win rate.png')
#     ggsave(p2, 'agents score.png')
#
#
# def draw_monte_sanity_check():
#     """
#     use the results from the excel to draw graphs of the win rate and score of
#     monte carlo vs himself
#     """
#     df1 = pd.DataFrame(
#         {
#             "depth": [4, 6, 8],
#             "score rate": [0.5958335, 0.8125, 0.9166665],
#             "win rate": [0.15, 0.55, 0.8],
#             "heuristic": "H4"
#         }
#     )
#     df2 = pd.DataFrame(
#         {
#             "depth": [4, 6, 8],
#             "score rate": [0.645833, 0.916667, 0.9916665],
#             "win rate": [0.05, 0.5, 0.95],
#             "heuristic": "H5"
#         }
#     )
#     df = pd.concat([df1, df2])
#     p1 = ggplot(df) + geom_line(aes(x='depth', y='score rate', color="heuristic")) +\
#          geom_point(aes(x='depth', y='score rate', color="heuristic")) \
#          + ggtitle("Score Rate of MCST agents over the agents' depth") \
#          + labs(x='depth', y='score rate')
#     p2 = ggplot(df) + geom_line(aes(x='depth', y='win rate', color="heuristic")) + \
#          geom_point(aes(x='depth', y='win rate', color="heuristic")) \
#          + ggtitle("Win Rate of MCST agents over the agents' depth") \
#          + labs(x='depth', y='win rate')
#     print(p1)
#     print(p2)
#     ggsave(p1, 'MCSTagents win rate.png')
#     ggsave(p2, 'MCSTagents score rate.png')
#
# def draw_minimax_sanity_check():
#     df1 = pd.DataFrame(
#         {
#             "depth": [1, 2, 3],
#             "score rate": [0, 0, 0],
#             "win rate": [0, 0, 0],
#             "heuristic": "H4"
#         }
#     )
#     df2 = pd.DataFrame(
#         {
#             "depth": [1, 2, 3],
#             "score rate": [0, 0.020833333, 0.020833333],
#             "win rate": [0, 0.25, 0.25],
#             "heuristic": "H5"
#         }
#     )
#     df = pd.concat([df1, df2])
#     p1 = ggplot(df) + geom_line(aes(x='depth', y='score rate', color="heuristic")) + geom_point(
#         aes(x='depth', y='score rate', color="heuristic")) \
#          + ggtitle("Score Rate of Minimax agents over the agents' depth") \
#          + labs(x='depth', y='score rate')
#     p2 = ggplot(df) + geom_line(aes(x='depth', y='win rate', color="heuristic")) + geom_point(
#         aes(x='depth', y='win rate', color="heuristic")) \
#          + ggtitle("Win Rate of Minimax agents over the agents' depth") \
#          + labs(x='depth', y='win rate')
#     print(p1)
#     print(p2)
#     ggsave(p1, 'MINIagents win rate.png')
#     ggsave(p2, 'MINIagents score rate.png')
