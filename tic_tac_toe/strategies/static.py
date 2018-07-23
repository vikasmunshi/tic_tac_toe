#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/static.py
import atexit
import collections
import json
import operator
import os.path
import random
import string

from tic_tac_toe import Board, Cell, cached


@cached
def cells_to_chars(board_size: int, board_moves) -> str:
    return ''.join(get_board_chars(board_size)[cell[1] + cell[0] * board_size] for cell in board_moves)


@cached
def char_to_cell(size: int, move_char: str) -> (int, int):
    return get_board_chars(size).index(move_char) // size, get_board_chars(size).index(move_char) % size


@cached
def get_board_center_char(size: int) -> str:
    return '' if size % 2 == 0 else string.ascii_lowercase[(size * size) // 2]


@cached
def get_board_chars(size: int) -> str:
    return string.ascii_lowercase[:size * size]


@cached
def get_board_lines(board_size: int) -> (str, ...):
    return tuple(get_rotated_boards(board_size)[0][i::board_size] for i in range(board_size)) + \
           tuple(get_rotated_boards(board_size)[3][i::board_size] for i in range(board_size)) + \
           (''.join(get_rotated_boards(board_size)[0][i * board_size + i] for i in range(board_size)),) + \
           (''.join(get_rotated_boards(board_size)[1][i * board_size + i] for i in range(board_size)),)


@cached
def get_board_orientation_map(size: int) -> {str: int}:
    return {
        c: 0 if c in get_rotated_boards(size)[0][:size * (size // 2)]
        else 1 if c in get_rotated_boards(size)[1][:size * (size // 2)]
        else 2 if c in get_rotated_boards(size)[2][:size * (size // 2)]
        else 3 if c in get_rotated_boards(size)[3][:size * (size // 2)]
        else 0
        for c in get_board_chars(size)}


@cached
def get_board_rotation_maps(size: int) -> (str, str, str, str):
    return tuple(dict(zip(get_rotated_boards(size)[i], get_board_chars(size))) for i in range(4))


@cached
def get_corner_cells(size: int) -> str:
    return ''.join(b[0] for b in get_rotated_boards(size))


@cached
def get_defensive_moves(board_size: int, moves_str: str) -> str:
    return ''.join(c for c in get_possible_moves(board_size, moves_str)
                   if last_move_has_won(board_size, moves_str + ' ' + c))


@cached
def get_orientation(size: int, moves: str) -> int:
    return 0 if len(moves) == 0 or (len(moves) == 1 and moves[0] == get_board_center_char(size)) else \
        get_board_orientation_map(size)[moves[1] if moves[0] == get_board_center_char(size) else moves[0]]


@cached
def get_possible_moves(size: int, moves: str) -> str:
    return ''.join(c for c in get_board_chars(size) if c not in moves)


@cached
def get_rotated_boards(size) -> (str, str, str, str):
    rotated_boards = (get_board_chars(size),)
    for _ in range(3):
        rotated_boards += (''.join(rotated_boards[-1][i % size::size] for i in range(-1, -size - 1, -1)),)
    return rotated_boards


@cached
def get_trap_moves(board_size: int, moves_str: str) -> str:
    return ''.join(c for c in get_possible_moves(board_size, moves_str)
                   if len(get_winning_moves(board_size, moves_str + c + ' ')) > 1)


@cached
def get_winning_moves(board_size: int, moves_str: str) -> str:
    return ''.join(c for c in get_possible_moves(board_size, moves_str) if last_move_has_won(board_size, moves_str + c))


@cached
def last_move_has_won(board_size: int, moves_str: str) -> bool:
    return any([all([c in moves_str[1 - len(moves_str) % 2::2] for c in l]) for l in get_board_lines(board_size)])


@cached
def rotate(board_size: int, moves_str: str, turns: int) -> str:
    return ''.join(get_board_rotation_maps(board_size)[turns % 4][c] for c in moves_str) if moves_str else ''


@cached
def setup_func(board_size: int) -> (callable, callable, callable):
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '_{0}x{0}.json'.format(board_size))
    try:
        with open(fn) as infile:
            cache = json.load(infile)
    except (FileNotFoundError,):
        cache = {
            '': 'acgi',
            'a': 'e', 'b': 'ac', 'c': 'e', 'e': 'acgi',
            'ab': 'e', 'ac': 'gi', 'ad': 'e', 'ae': 'i', 'af': 'e', 'ag': 'ci', 'ah': 'e', 'ai': 'cg',
            'ca': 'gi', 'cb': 'e', 'cd': 'e', 'ce': 'g', 'cf': 'e', 'cg': 'ai', 'ch': 'e', 'ci': 'ag'
        } if board_size == 3 else {}

    def dump() -> None:
        with open(fn, 'w') as outfile:
            json.dump(
                collections.OrderedDict(sorted(((k, ''.join(sorted(v)))
                                                for k, v in cache.items()), key=operator.itemgetter(0))),
                outfile,
                indent=4,
                separators=(',', ': ')
            )

    def get_moves(board_str: str) -> str:
        return cache.get(board_str, '')

    def put_moves(board_str: str, moves_str: str) -> None:
        cache[board_str] = moves_str
        atexit.unregister(dump)
        atexit.register(dump)

    def del_moves(loosing_board: str) -> None:
        for k, m in ((loosing_board[:i], loosing_board[i])
                     for i in range((2 if board_size == 3 else 0) + (len(loosing_board) % 2), len(loosing_board), 2)):
            cache[k] = cache[k].replace(m, '')
        atexit.unregister(dump)
        atexit.register(dump)

    return get_moves, put_moves, del_moves


def strategy(board: Board) -> Cell:
    get_moves, put_moves, del_moves = setup_func(board.size)
    moves_orig = cells_to_chars(board.size, board.moves)
    orientation = get_orientation(board.size, moves_orig)
    moves = rotate(board.size, moves_orig, orientation)
    next_moves = get_moves(moves)
    if next_moves == '':
        next_moves = get_winning_moves(board.size, moves) or \
                     get_defensive_moves(board.size, moves) or \
                     get_trap_moves(board.size, moves) or \
                     get_possible_moves(board.size, moves)
        put_moves(moves, next_moves)

    for new_board in (moves + m for m in next_moves):
        if not (last_move_has_won(board.size, new_board) or get_winning_moves(board.size, new_board) == ''):
            del_moves(moves)

    return Cell(*char_to_cell(board.size, rotate(board.size, random.choice(next_moves), - orientation)))
