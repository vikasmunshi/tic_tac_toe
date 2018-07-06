#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/static_3x3_gen.py
import atexit
import collections
import json
import os.path
import random

from tic_tac_toe import *

board_center_char = 'e'
board_chars = 'abcdefghi'
board_size = 3
board_to_move = {}
board_to_move_base = {
    '': 'acgi',
    'a': 'e', 'b': 'ac', 'c': 'e', 'e': 'acgi',
    "ab": "e", "ac": "gi", "ad": "e", "ae": "i", "af": "e", "ag": "ci", "ah": "e", "ai": "cg",
    "ca": "gi", "cb": "e", "cd": "e", "ce": "g", "cf": "e", "cg": "ai", "ch": "e", "ci": "ag",
}


@cached
def board_to_move_dump() -> None:
    with open(os.path.abspath(os.path.splitext(__file__)[0] + '.json'), 'w') as outfile:
        json.dump(
            collections.OrderedDict(sorted(board_to_move.items(), key=lambda i: (len(i[0]), i[0]))),
            outfile,
            indent=4,
            separators=(',', ': ')
        )


@cached
def board_to_move_load() -> None:
    global board_to_move
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '.json')
    if os.path.exists(fn):
        with open(fn) as infile:
            board_to_move = json.load(infile)
    board_to_move.update(board_to_move_base)


@cached
def cells_to_chars(cells):
    return ''.join(board_chars[cell[1] + cell[0] * board_size] for cell in cells)


@cached
def char_to_cell(cell_str: str) -> Cell:
    return Cell(board_chars.index(cell_str) // board_size, board_chars.index(cell_str) % board_size)


@cached
def get_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def get_orientation(moves_str):
    if len(moves_str) == 0 or (len(moves_str) == 1 and moves_str[0] == board_center_char):
        return 0
    else:
        return {
            'a': 0, 'b': 0, 'c': 0, 'd': 3, 'f': 1, 'g': 3, 'h': 2, 'i': 1
        }[moves_str[1] if moves_str[0] == board_center_char else moves_str[0]]


@cached
def get_trap_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board)
                 if len(get_winning_moves(Board(board.size, board.moves + (c, ())))) > 1)


@cached
def get_winning_moves(board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


@cached
def rotate(moves_str, turns):
    for _ in range(turns % 4):
        moves_str = ''.join({'a': 'g', 'b': 'd', 'c': 'a',
                             'd': 'h', 'e': 'e', 'f': 'b',
                             'g': 'i', 'h': 'f', 'i': 'c'}[c] for c in moves_str)
    return moves_str


def strategy(board: Board) -> Cell:
    global board_to_move
    board_str_orig = cells_to_chars(tuple(Cell(*c) for c in board.moves))
    orientation = get_orientation(board_str_orig)
    board_str = rotate(board_str_orig, orientation)
    moves_str = board_to_move.get(board_str)
    if moves_str is None or moves_str == '':
        moves = get_winning_moves(board) or \
                get_defensive_moves(board) or \
                get_trap_moves(board) or \
                get_possible_moves(board)
        moves_str = rotate(cells_to_chars(moves), orientation)
        board_to_move[board_str] = ''.join(sorted(moves_str))
        atexit.register(board_to_move_dump)

    move = char_to_cell(rotate(random.choice(moves_str), -orientation))

    new_board = Board(board.size, board.moves + (move,))
    if not last_move_has_won(new_board):
        if get_winning_moves(new_board):
            for k, m in ((board_str[:i], board_str[i]) for i in range(2 + (len(board_str) % 2), len(board_str), 2)):
                board_to_move[k] = ''.join(c for c in board_to_move[k] if c != m)
            atexit.register(board_to_move_dump)

    return move


board_to_move_load()
