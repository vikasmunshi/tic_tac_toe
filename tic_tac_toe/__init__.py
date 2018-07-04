#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__init__.py
from .core import get_cells, get_lines, get_possible_moves, last_move_has_won, strategy
from .tournament import play_tournament_eliminate, play_tournament_points
from .user_types import Board, Cell, Cells, Lines, Player, Players, Scores
from .util import cached, select_random_cell

__package__ = 'tic_tac_toe'
__version__ = '1.5.1'
memoize = cached
__all__ = (
    'get_cells', 'get_lines', 'get_possible_moves', 'last_move_has_won', 'strategy',
    'play_tournament_eliminate', 'play_tournament_points',
    'Board', 'Cell', 'Cells', 'Lines', 'Player', 'Players', 'Scores',
    'cached', 'select_random_cell',
    'memoize'
)
