#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
import itertools
import operator
import os.path
import os.path
import pickle
import typing

from .types import Board, Cells, Game, Moves, TypeFuncBoard

cache = set()


def dump_cache(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(cache, outfile)


def load_cache(cache_name: str, size: int) -> bool:
    global cache
    cache_file = os.path.abspath(os.path.splitext(cache_name)[0] + '.memory_{0}x{0}.pickle'.format(size))
    atexit.register(dump_cache, cache_file=cache_file)
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as infile:
            cache = pickle.load(infile)
        return True
    return False


def recollect(moves: Moves) -> typing.Iterable[Game]:
    return (game for game in cache if game.moves[:len(moves)] == moves)


def remember_game(game: Game) -> None:
    global cache
    cache.add(game)


def remembered(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            remember_game(Game(moves=board.moves, result=result))
        return result

    return f


def suggest_moves(board: Board, possible_moves: Cells) -> Cells:
    if len(possible_moves) > 1:
        move_num = len(board.moves)

        def get_bucket(game: Game) -> str:
            return 'D' if game.result == 'D' else 'W' if game.result == ('X', 'O')[move_num % 2] else 'L'

        weights = zip(((0, -2, 1), (1, -3, 1))[move_num % 2], ('D', 'L', 'W'))
        moves = {bucket: tuple(game.moves[move_num] for game in games)
                 for bucket, games in itertools.groupby(sorted(recollect(board.moves), key=get_bucket), key=get_bucket)}
        scores = {move: sum(wt * moves.get(b, ()).count(move) for wt, b in weights) for move in possible_moves}
        max_score = max(scores.items(), key=operator.itemgetter(1))[1]
        return tuple(m for m in possible_moves if scores[m] == max_score)
    return possible_moves
