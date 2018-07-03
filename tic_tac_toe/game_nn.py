#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/game_nn.py
import atexit
import collections
import os.path
import pickle

import numpy as np

from tic_tac_toe.user_types import Board, Cell, Cells, Game, TypeFuncBoard
from tic_tac_toe.util import cached, select_random_cell

nn = []
nn_training_data = collections.defaultdict(tuple)


def add_game_to_nn(game: Game) -> None:
    global nn_training_data
    if game.result in ('X', 'O'):
        for i in tuple(range(0 if game.result == 'X' else 1, len(game.moves), 2)):
            nn_training_data[game.moves[0:i]] += (game.moves[i],)


@cached
def dump_nn(cache_file: str, size: int) -> None:
    train_nn(size)
    with open(cache_file, 'wb') as outfile:
        pickle.dump(nn, outfile)


@cached
def load_nn(cache_name: str, size: int) -> bool:
    global nn
    cache_file = os.path.abspath(os.path.splitext(cache_name)[0] + '.nn_{0}x{0}.pickle'.format(size))
    atexit.register(dump_nn, cache_file=cache_file, size=size)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as infile:
                nn = pickle.load(infile)
        except (EOFError, FileNotFoundError, IOError, ModuleNotFoundError):
            return True
        else:
            return False
    return True


@cached
def nn_board_to_vector(board: Board) -> np.ndarray:
    board_vector = np.zeros(board.size ** 2, dtype=int)
    for i, cell in enumerate(board.moves):
        board_vector[cell.col_id + cell.row_id * board.size] = 1 + i % 2
    return board_vector


@cached
def nn_cell_to_vector(cell: Cell, size: int) -> np.ndarray:
    board_vector = np.zeros(size ** 2, dtype=int)
    board_vector[cell.col_id + cell.row_id * size] = 1
    return board_vector


def nn_sigmoid(x: np.ndarray, derivative: bool = False) -> np.ndarray:
    return x * (1 - x) if derivative else 1 / (1 + np.exp(-x))


def nn_vector_to_cell(v: np.ndarray, size: int) -> Cell:
    cell_num = np.argmax(v)
    return Cell(row_id=cell_num // size, col_id=cell_num % size)


def remembered_in_nn(func: TypeFuncBoard) -> TypeFuncBoard:
    global nn_training_data

    def f(board: Board) -> str:
        result = func(board)
        add_game_to_nn(Game(moves=board.moves, result=result))
        return result

    return f


def setup_nn(cache_name: str, size: int) -> None:
    if load_nn(cache_name, size):
        global nn
        nn = [
            2 * np.random.random((size ** 2, size ** 3)) - 1,
            2 * np.random.random((size ** 3, size ** 2)) - 1
        ]


def suggest_move_nn(board: Board, possible_moves: Cells) -> Cell:
    l0 = nn_board_to_vector(board)
    l1 = nn_sigmoid(np.dot(l0, nn[0]))
    l2 = nn_sigmoid(np.dot(l1, nn[1]))
    move = nn_vector_to_cell(l2, board.size)
    if move in possible_moves:
        return move
    else:
        print('nn will return a random move')
        return select_random_cell(possible_moves)


def train_nn(size: int) -> None:
    global nn, nn_training_data
    if nn_training_data:
        data_input = np.array([nn_board_to_vector(Board(size, moves)) for moves in nn_training_data.keys()])
        data_output = np.array([nn_cell_to_vector(max(next_move, key=next_move.count), size)
                                for next_move in nn_training_data.values()])
        nn_training_data.clear()
        for i in range(10001):
            l0 = data_input
            l1 = nn_sigmoid(np.dot(l0, nn[0]))
            l2 = nn_sigmoid(np.dot(l1, nn[1]))
            l2_error = data_output - l2
            l2_delta = l2_error * nn_sigmoid(l2, derivative=True)
            l1_error = l2_delta.dot(nn[1].T)
            l1_delta = l1_error * nn_sigmoid(l1, derivative=True)

            nn[1] += l1.T.dot(l2_delta)
            nn[0] += l0.T.dot(l1_delta)

            if i % 1000 == 0:
                print('err:', i, np.mean(np.abs(l2_error)), l0.size)
