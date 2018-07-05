#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/dictionary_3.py
import atexit
import collections
import json
import os.path
import string

from tic_tac_toe import *

base_board_3x3 = {
    '': 'acgi',
    'a': 'e', 'b': 'ac', 'c': 'e', 'd': 'ag', 'e': 'acgi', 'f': 'ci', 'g': 'e', 'h': 'gi', 'i': 'e',
    'ab': 'e', 'ac': 'gi', 'ad': 'e', 'ae': 'i', 'af': 'e', 'ag': 'ci', 'ah': 'e', 'ai': 'cg',
    'ca': 'gi', 'cb': 'e', 'cd': 'e', 'ce': 'g', 'cf': 'e', 'cg': 'ai', 'ch': 'e', 'ci': 'ag',
    'ga': 'ci', 'gb': 'e', 'gc': 'ai', 'gd': 'e', 'ge': 'c', 'gf': 'e', 'gh': 'e', 'gi': 'ac',
    'ia': 'cg', 'ib': 'e', 'ic': 'ag', 'id': 'e', 'ie': 'a', 'if': 'e', 'ig': 'ac', 'ih': 'e'
}
board_3x3 = {}
board_size = 3


@cached
def board_3x3_dump() -> None:
    with open(os.path.abspath(os.path.splitext(__file__)[0] + '.json'), 'w') as outfile:
        json.dump(
            collections.OrderedDict(sorted(board_3x3.items(), key=lambda i: (len(i[0]), i[0]))),
            outfile,
            indent=4,
            separators=(',', ': ')
        )


@cached
def board_3x3_load() -> None:
    global board_3x3
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '.json')
    if os.path.exists(fn):
        with open(fn) as infile:
            board_3x3 = json.load(infile)
            board_3x3.update(base_board_3x3)
    else:
        board_3x3 = dict(base_board_3x3)


@cached
def cells_to_chars(cells: Cells) -> str:
    return ''.join(string.ascii_lowercase[cell.col_id + cell.row_id * board_size] for cell in cells) if cells else ''


@cached
def char_to_cell(char: str) -> Cell:
    return Cell(row_id=char_to_cell_num(char) // board_size, col_id=char_to_cell_num(char) % board_size) if char else ()


@cached
def char_to_cell_num(char: str) -> int:
    return string.ascii_lowercase.index(char)


@cached
def chars_to_cells(chars: str) -> Cells:
    return tuple(char_to_cell(c) for c in chars) if chars else ''


@cached
def get_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def get_trap_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board)
                 if len(get_winning_moves(Board(board.size, board.moves + (c, ())))) > 1)


@cached
def get_winning_moves(board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


def strategy(board: Board) -> Cell:
    global board_3x3
    board_str = cells_to_chars(tuple(Cell(*c) for c in board.moves))
    moves_str = board_3x3.get(board_str)
    if moves_str is None or moves_str == '':
        moves = get_winning_moves(board) or \
                get_defensive_moves(board) or \
                get_trap_moves(board) or \
                get_possible_moves(board)
        moves_str = cells_to_chars(moves)
        board_3x3[board_str] = moves_str
        atexit.register(board_3x3_dump)

    r = select_random_cell(chars_to_cells(moves_str))

    new_board = Board(board.size, board.moves + (r,))
    if not last_move_has_won(new_board):
        if get_winning_moves(new_board):
            for k, m in ((board_str[:i], board_str[i]) for i in range(2 + (len(board_str) % 2), len(board_str), 2)):
                if len(board_3x3[k]) > 1:
                    board_3x3[k] = ''.join(c for c in board_3x3[k] if c != m)
            atexit.register(board_3x3_dump)

    return r


board_3x3_load()
