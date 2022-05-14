from Board import Surakarta
from Player import HumanPlayer, RandomPlayer, MiniMaxPlayer, MonteCarloPlayer, \
    Player
from Heuristics import basic_heuristic, position_heuristic, attack_heuristic, \
    defensive_heuristic, smart_heuristic
from GUI import GUI, NotGUI

PLAYERS_HEURISTICS = {
    'H1': attack_heuristic,
    'H2': defensive_heuristic,
    'H3': position_heuristic,
    'H4': basic_heuristic,
    'H5': smart_heuristic
}


def build_MCST_agent() -> MonteCarloPlayer:
    """
    :return: a monte carlo with the user chosen parameters
    """
    depth = int(input('Choose the depth of this agent: '))
    num_simulations = int(input('Choose the number of simulations: '))
    heuristic = PLAYERS_HEURISTICS[input('Choose heuristic (H1, H2, H3, H4, H5): ')]
    return MonteCarloPlayer(depth, num_simulations, heuristic)


def build_MINIMAX_agent() -> MiniMaxPlayer:
    """
    :return: a minimax with the user chosen parameters
    """
    depth = int(input('Choose the depth of this agent: '))
    heuristic = PLAYERS_HEURISTICS[input('Choose heuristic (H1, H2, H3, H4, H5): ')]
    return MiniMaxPlayer(depth, heuristic)


def get_player(is_gui: bool) -> Player:
    """
    :param is_gui: a boolean if the user wants to use gui
    :return: the player that the user wants
    """
    player = input('Choose the type of the player (MCST, MINIMAX, HUMAN, RANDOM): ')
    if player == "MCST":
        player = build_MCST_agent()
    elif player == "MINIMAX":
        player = build_MINIMAX_agent()
    elif player == "HUMAN":
        player = HumanPlayer(is_gui)
    elif player == "RANDOM":
        player = RandomPlayer()
    else:
        print("BAD PLAYER'S TYPE")
        exit()
    return player


if __name__ == '__main__':
    print('There are 4 kinds of players: MCST, MINIMAX, HUMAN and RANDOM.\n'
          'Each agent has its own relevant parameters.')
    print('There are 5 different heuristics:')
    print('    - H1: attack heuristic')
    print('    - H2: defence heuristic')
    print('    - H3: position heuristic')
    print('    - H4: attack-defence heuristic')
    print('    - H5: smart attack-defence-position heuristic')
    print()
    is_gui = input('Do you want GUI (y / n)? ') == 'y'
    print('=== Choose the first player (red player) ===')
    player1 = get_player(is_gui)
    print('=== Choose the second player (black player) ===')
    player2 = get_player(is_gui)
    surakarta = Surakarta(player2, player1)
    if is_gui:
        gui = GUI(surakarta)
    else:
        gui = NotGUI(surakarta)
    gui.run()
