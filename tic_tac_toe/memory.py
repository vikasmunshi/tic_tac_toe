#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
import os.path
import pickle

from .types import Board, Game, Moves, TypeFuncBoard
from .util import cached

cache = {'moves': {}, 'games': set()}


def dump_cache(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(cache, outfile)


def load_cache(cache_file: str) -> bool:
    global cache
    atexit.register(dump_cache, cache_file=cache_file)
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as infile:
            cache = pickle.load(infile)
        return True

    return False


def recollect(moves: Moves) -> dict:
    return dict(cache['moves'].get(moves, {}))


def remember_game(game: Game, size: int) -> None:
    global cache
    if not game in cache['games']:
        for slider in range(0, len(game)):
            moves, next_move = game.moves[:slider], game.moves[slider]
            if not moves in cache['moves']: cache['moves'][moves] = {}
            if not next_move in cache['moves'][moves]: cache['moves'][moves][next_move] = 0
            cache['moves'][game.moves[:slider]][next_move] += \
                (0 if game.result == 'D' else 1 if game.result == ('X', 'O')[slider % 2] else -1) * \
                2 ** score_move(size)[len(game.moves) - slider]
        cache['games'].add(game)


def remembered(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            remember_game(Game(moves=board.moves, result=result), size=board.size)
        return result

    return f


@cached
def score_move(size):
    return tuple(x for x in range(size * size + 1, 0, -1))
