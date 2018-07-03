#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#   tic_tac_toe/strategies/ml.py
from tic_tac_toe import *


@memoize
def cost_function(board, move):
    b = Board(board.size, board.moves + (move,))
    p = len(b.moves) % 2
    return 1 * count_free_lines(get_lines(b), b.moves[1 - p::2]) - 1 * count_free_lines(get_lines(b), b.moves[p::2])


@memoize
def count_free_lines(lines, moves):
    return len(tuple(l for l in lines if not any(m in l for m in moves)))


@memoize
def get_cost_optimal_moves(board) :
    return tuple(c[0] for c in get_costs(board) if c[1] == get_costs_min_cost(board))


@memoize
def get_costs(board):
    return tuple((move, cost_function(board, move)) for move in get_possible_moves(board))


@memoize
def get_costs_min_cost(board):
    return min(get_costs(board), key=operator.itemgetter(1))[1]


@memoize
def get_defensive_moves(board) :
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@memoize
def get_winning_moves(board) :
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


def strategy(board):
    return select_random_cell(get_winning_moves(board) or get_defensive_moves(board) or get_cost_optimal_moves(board))
