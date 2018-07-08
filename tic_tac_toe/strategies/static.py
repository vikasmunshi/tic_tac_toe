#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/static.py
import json
import os.path
import random
import string

board_center_char = ''
board_chars = ''
board_orientation_map = {}
board_rotation_maps = ()
board_size = 0


def board_to_move(moves_str):
    return {}[moves_str]


def cached(func):
    cache = {}

    def f(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return f


@cached
def cells_to_chars(moves):
    return ''.join(board_chars[cell[1] + cell[0] * board_size] for cell in moves)


@cached
def char_to_cell(char):
    return board_chars.index(char) // board_size, board_chars.index(char) % board_size


@cached
def get_orientation(moves_str):
    return 0 if len(moves_str) == 0 or (len(moves_str) == 1 and moves_str[0] == board_center_char) else \
        board_orientation_map[moves_str[1] if moves_str[0] == board_center_char else moves_str[0]]


@cached
def load_board_to_move(size: int) -> None:
    global board_to_move
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '_gen_{0}x{0}.json'.format(size))
    if os.path.exists(fn):
        with open(fn) as infile:
            board_to_move_dict = json.load(infile)
        board_to_move = lambda moves_str: board_to_move_dict[moves_str]


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


def strategy(board):
    setup_board(board.size)
    board_moves = cells_to_chars(board.moves)
    orientation = get_orientation(board_moves)
    next_move = random.choice(board_to_move(rotate(board_moves, orientation)))
    return char_to_cell(rotate(next_move, - orientation))
