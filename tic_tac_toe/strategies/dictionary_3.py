#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tic_tac_toe/strategies/dictionary_3.py
import json
import os.path
import string

from tic_tac_toe import *

board_size = 3
board_3x3 = {}


@cached
def cells_to_char(cells: Cells) -> str:
    return ''.join(string.ascii_lowercase[cell.col_id + cell.row_id * board_size] for cell in cells) if cells else ''


@cached
def char_to_cell(char: str) -> Cell:
    return Cell(row_id=char_to_cell_num(char) // board_size, col_id=char_to_cell_num(char) % board_size) if char else ()


@cached
def char_to_cell_num(char: str) -> int:
    return string.ascii_lowercase.index(char)


@cached
def dict_load() -> None:
    global board_3x3
    fn = os.path.abspath(os.path.splitext(__file__)[0] + '.json')
    if os.path.exists(fn):
        with open(fn) as infile:
            board_3x3 = json.load(infile)


def strategy(board: Board) -> Cell:
    return char_to_cell(select_random_cell(board_3x3.get(cells_to_char(board.moves)) or get_possible_moves(board))) \
        if board.size == board_size else select_random_cell(get_possible_moves(board))


dict_load()
