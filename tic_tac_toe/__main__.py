#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__main__.py
import argparse
import glob
import importlib.util
import inspect
import os
import time

from .core import re_memorize_games, strategy
from .tournament import play_tournament_eliminate, play_tournament_points
from .types import Player, Players

os.environ['COLUMNS'] = '120'


def load_players(players_folder: str, include_bad: bool = False, ignore_signature: bool = False) -> Players:
    expected_signature = inspect.signature(strategy)
    for player_file in glob.iglob(os.path.join(players_folder, '[!_]*.py')):
        player_name = os.path.splitext(os.path.basename(player_file))[0]
        try:
            if not include_bad and player_name.startswith('bad'):
                continue
            player_strategy_spec = importlib.util.spec_from_file_location(player_name, player_file)
            player_strategy_module = importlib.util.module_from_spec(player_strategy_spec)
            player_strategy_spec.loader.exec_module(player_strategy_module)
            player_strategy = getattr(player_strategy_module, 'strategy')
            assert inspect.isfunction(player_strategy), \
                'strategy is {} and not function'.format(type(player_strategy).__name__)
            assert ignore_signature or inspect.signature(player_strategy) == expected_signature, \
                'signature is not strategy{}'.format(expected_signature)
            yield Player(player_name, player_strategy)
        except (AssertionError, AttributeError, ImportError, SyntaxError, TypeError) as e:
            print('{} ignored because {}'.format(player_name, str(e)))


def main() -> str:
    parser = argparse.ArgumentParser(description='Play Tic Tac Toe Tournament')

    parser.add_argument('-b', dest='board_size', type=int, default=3,
                        help='board size, default is 3')
    parser.add_argument('-d', dest='strategies_folder', type=str,
                        help='location of player strategy files, default is TIC_TAC_TOE_DIR/strategies')
    parser.add_argument('-g', dest='games', default=1000, type=int,
                        help='number of games per match, default is 1000')
    parser.add_argument('-t', dest='tournament_type', choices=('fight', 'points'), default='fight',
                        help='fight for elimination or play for points, default is elimination')
    parser.add_argument('--include_bad', action='store_true',
                        help='include files matching bad*.py in strategies folder, ignored by default')
    parser.add_argument('--py2', action='store_true',
                        help='also load python 2 strategy files')

    args = parser.parse_args()
    strategies_folder = args.strategies_folder or os.path.join(os.path.dirname(__file__), 'strategies')
    re_memorize_games(args.board_size)
    if args.tournament_type == 'fight':
        winners = play_tournament_eliminate(
            size=args.board_size,
            num_games=args.games,
            players=tuple(load_players(strategies_folder, args.include_bad, args.py2)),
            round_num=0
        )
        return (
            'Winner is {}\n'.format(winners[0].name) if len(winners) == 1 else
            'Winners are {}\n'.format(', '.join([player.name for player in winners]))
        )
    else:
        scores = play_tournament_points(
            size=args.board_size,
            num_games=args.games,
            players=tuple(load_players(strategies_folder, args.include_bad, args.py2))
        )
        longest_name_length = max([len(score.player) for score in scores])
        l = '{:' + str(longest_name_length + 2) + 's}{:9d} {:9.2%} {:9d} {:9d} {:9d} {:9d}\n'
        h = '{:' + str(longest_name_length + 2) + 's}{}\n'
        return (
            h.format('Player', '   Points   Wins(%)    Losses     Draws     Games Penalties') +
            ''.join([l.format(s.player, s.points, s.wins / (s.games or 1), s.losses, s.draws, s.games, s.penalties)
                     for s in scores])
        )


if __name__ == '__main__':
    st = time.time()
    result = main()
    et = time.time()
    print('Tournament completed in {0:0.4f} seconds'.format(et - st))
    print('\n' + result)
