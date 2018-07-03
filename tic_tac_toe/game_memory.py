#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/game_memory.py
import atexit
import itertools
import operator
import os.path
import pickle
import typing

from .user_types import Board, Cells, Game, Moves, TypeFuncBoard
from .util import cached

memory = set()


@cached
def add_game_to_memory(game: Game) -> None:
    global memory
    memory.add(game)


@cached
def dump_memory(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(memory, outfile)


@cached
def load_memory(cache_name: str, size: int) -> bool:
    global memory
    cache_file = os.path.abspath(os.path.splitext(cache_name)[0] + '.memory_{0}x{0}.pickle'.format(size))
    atexit.register(dump_memory, cache_file=cache_file)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as infile:
                memory = pickle.load(infile)
        except (EOFError, FileNotFoundError, IOError, ModuleNotFoundError):
            return True
        else:
            return False
    return True


def recollect(moves: Moves) -> typing.Iterable[Game]:
    return (game for game in memory if game.moves[:len(moves)] == moves)


def remembered_in_memory(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            add_game_to_memory(Game(moves=board.moves, result=result))
        return result

    return f


@cached
def suggest_moves_memory(board: Board, possible_moves: Cells) -> Cells:
    if len(possible_moves) > 1:
        move_num = len(board.moves)
        end_win = ('X', 'O')[len(board.moves) % 2]

        @cached
        def get_game_result(game: Game) -> str:
            return 'D' if game.result == 'D' else 'W' if game.result == end_win else 'L'

        recollected_games = sorted(recollect(board.moves), key=get_game_result)
        grouped_moves = {result: tuple(game.moves[move_num] for game in games)
                         for result, games in itertools.groupby(recollected_games, key=get_game_result)}
        draws = set(grouped_moves.get('D', ()))
        losses = set(grouped_moves.get('L', ()))
        wins = set(grouped_moves.get('W', ()))

        assured_wins = wins - draws - losses
        if assured_wins:
            return tuple(assured_wins)

        assured_no_loss = (wins | draws) - losses
        if assured_no_loss:
            return tuple(assured_no_loss)

        weights = zip(((0, -2, 1), (1, -3, 1))[move_num % 2], ('D', 'L', 'W'))
        scores = {move: sum(weight * grouped_moves.get(result, ()).count(move) for weight, result in weights)
                  for move in possible_moves}
        max_score = max(scores.items(), key=operator.itemgetter(1))[1]
        return tuple(m for m in possible_moves if scores[m] == max_score)

    return possible_moves
