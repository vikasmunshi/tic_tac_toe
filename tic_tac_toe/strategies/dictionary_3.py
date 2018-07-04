#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/hard_coded_3.py
import atexit
import json
import os.path
import string

from tic_tac_toe import *

board_size = 3
board_3 = {}


@cached
def cells_to_char(cells: Cells) -> str:
    return ''.join(string.ascii_lowercase[cell.col_id + cell.row_id * board_size] for cell in cells) if cells else ''


@cached
def char_to_cell(char: str) -> Cell:
    if char:
        cell_num = string.ascii_lowercase.index(char)
        return Cell(row_id=cell_num // board_size, col_id=cell_num % board_size)
    return ()


@cached
def dict_dump() -> None:
    with open(os.path.abspath(os.path.splitext(__file__)[0] + '.json'), 'w') as outfile:
        json.dump(board_3, outfile)


@cached
def dict_load() -> None:
    global board_3
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '.json')
    if os.path.exists(fn):
        with open(fn) as infile:
            board_3 = json.load(infile)
    atexit.register(dict_dump)


def strategy(board: Board) -> Cell:
    return char_to_cell(select_random_cell(board_3[cells_to_char(board.moves)]))


dict_load()
