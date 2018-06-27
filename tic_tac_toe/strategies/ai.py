#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/strategies/ai.py
from itertools import groupby, permutations
from os.path import abspath, splitext

from tic_tac_toe.core import get_cells, get_possible_moves, last_move_has_won
from tic_tac_toe.memory import load_cache, recollect, remember_game
from tic_tac_toe.types import Board, Cell, Cells, Game
from tic_tac_toe.util import cached, select_random_cell


@cached
def reduce_board(board: Board) -> Game:
    for subset_moves in (board.moves[0:n] for n in range(2 * board.size - 1, board.size * board.size + 1)):
        if last_move_has_won(Board(board.size, subset_moves)):
            return Game(moves=subset_moves, result=('O', 'X')[len(subset_moves) % 2])
    return Game(moves=board.moves, result='D')


@cached
def memorize_games(size: int) -> None:
    cache_file = abspath(splitext(__file__)[0] + '.{}.pickle'.format(size))
    if (not load_cache(cache_file)) and size < 4:
        for g in (reduce_board(Board(size, moves)) for moves in permutations(get_cells(Board(size=size, moves=())))):
            remember_game(g)


def suggest_moves(board) -> Cells:
    memorize_games(board.size)
    move_num = len(board.moves)

    def bucket(game: Game) -> str:
        return 'D' if game.result == 'D' else 'W' if game.result == ('X', 'O')[move_num % 2] else 'L'

    moves = {bucket: tuple(game.moves[move_num] for game in games)
             for bucket, games in groupby(sorted(recollect(board.moves), key=bucket), key=bucket)}
    return (
        tuple(move for move in moves.get('W', ()) if move not in moves.get('L', ())) or
        tuple(move for move in moves.get('W', ()) if move in moves.get('D', ()))
    )


def strategy(board: Board) -> Cell:
    return select_random_cell(suggest_moves(board) or get_possible_moves(board))
