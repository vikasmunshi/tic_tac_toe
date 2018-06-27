#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
import os.path
import pickle
from typing import Iterable

from .types import Board, Game, Moves, TypeFuncBoard

cache = set()


def dump_cache(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(cache, outfile)


def load_cache(cache_file: str) -> bool:
    global cache, graph
    atexit.register(dump_cache, cache_file=cache_file)
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as infile:
            cache = pickle.load(infile)
        return True
    return False


def recollect(moves: Moves) -> Iterable[Game]:
    return (game for game in cache if game.moves[:len(moves)] == moves)


def remember_game(game: Game) -> None:
    global cache, graph
    cache.add(game)


def remembered(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            remember_game(Game(moves=board.moves, result=result))
        return result

    return f
