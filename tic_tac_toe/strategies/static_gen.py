#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/static_3x3_gen.py
import atexit
import collections
import json
import operator
import os.path
import random
import string

from tic_tac_toe import Board, Cell, Cells, get_possible_moves, last_move_has_won

board_center_char = ''
board_chars = ''
board_orientation_map = {}
board_rotation_maps = ()
board_size = 0
board_to_move = {}


def cached(func):
    cache = {}

    def f(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return f


@cached
def cells_to_chars(cells):
    return ''.join(board_chars[cell[1] + cell[0] * board_size] for cell in cells)


@cached
def char_to_cell(cell_str: str) -> Cell:
    return Cell(board_chars.index(cell_str) // board_size, board_chars.index(cell_str) % board_size)


@cached
def dump_board_to_move(size: int) -> None:
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '_{0}x{0}.json'.format(size))
    with open(fn, 'w') as outfile:
        json.dump(
            collections.OrderedDict(sorted(board_to_move.items(), key=operator.itemgetter(0))),
            outfile,
            indent=4,
            separators=(',', ': ')
        )


@cached
def get_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def get_orientation(moves_str):
    return 0 if len(moves_str) == 0 or (len(moves_str) == 1 and moves_str[0] == board_center_char) else \
        board_orientation_map[moves_str[1] if moves_str[0] == board_center_char else moves_str[0]]


@cached
def get_trap_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board)
                 if len(get_winning_moves(Board(board.size, board.moves + (c, ())))) > 1)


@cached
def get_winning_moves(board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


@cached
def load_board_to_move(size: int) -> None:
    global board_to_move
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '_{0}x{0}.json'.format(size))
    if os.path.exists(fn):
        with open(fn) as infile:
            board_to_move = json.load(infile)


@cached
def rotate(moves_str, turns):
    return ''.join(board_rotation_maps[turns % 4][c] for c in moves_str) if moves_str else ''


@cached
def setup_board(size: int) -> None:
    global board_center_char, board_chars, board_orientation_map, board_rotation_maps, board_size
    board_center_char = '' if size % 2 == 0 else string.ascii_lowercase[(size * size) // 2]
    board_chars = string.ascii_lowercase[:size * size]
    rotated_boards = (board_chars,)
    for _ in range(3):
        rotated_boards += (''.join(rotated_boards[-1][i % size::size] for i in range(-1, -size - 1, -1)),)
    board_orientation_map = {
        c: 0 if c in rotated_boards[0][:size * (size // 2)]
        else 1 if c in rotated_boards[1][:size * (size // 2)]
        else 2 if c in rotated_boards[2][:size * (size // 2)]
        else 3 if c in rotated_boards[3][:size * (size // 2)]
        else 0
        for c in board_chars}
    board_rotation_maps = tuple(dict(zip(rotated_boards[i], board_chars)) for i in range(4))
    board_size = size
    load_board_to_move(size)


def strategy(board: Board) -> Cell:
    global board_to_move
    setup_board(board.size)
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
        atexit.register(dump_board_to_move, board.size)

    move = char_to_cell(rotate(random.choice(moves_str), -orientation))

    new_board = Board(board.size, board.moves + (move,))
    if not last_move_has_won(new_board):
        if get_winning_moves(new_board):
            for k, m in ((board_str[:i], board_str[i]) for i in range(2 + (len(board_str) % 2), len(board_str), 2)):
                board_to_move[k] = ''.join(c for c in board_to_move[k] if c != m)
            atexit.register(dump_board_to_move, board.size)

    return move
