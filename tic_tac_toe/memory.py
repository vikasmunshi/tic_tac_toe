#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
import os.path
import pickle
from itertools import groupby
from operator import itemgetter
from os.path import abspath, splitext
from typing import Iterable

from .types import Board, Cells, Game, Moves, TypeFuncBoard

cache = set()


def dump_cache(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(cache, outfile)


def load_cache(cache_name: str, size: int) -> bool:
    global cache
    cache_file = abspath(splitext(cache_name)[0] + '.memory_{0}x{0}.pickle'.format(size))
    atexit.register(dump_cache, cache_file=cache_file)
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as infile:
            cache = pickle.load(infile)
        return True
    return False


def recollect(moves: Moves) -> Iterable[Game]:
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
    move_num = len(board.moves)

    def bucket(game: Game) -> str:
        return 'D' if game.result == 'D' else 'W' if game.result == ('X', 'O')[move_num % 2] else 'L'

    recollected = sorted(recollect(board.moves), key=bucket)
    moves = {b: tuple(game.moves[move_num] for game in games) for b, games in groupby(recollected, key=bucket)}
    s = {
        move: 1000 * int(sum(
            w * moves.get(b, ()).count(move)
            for w, b in zip(((0, -2, 1), (1, -3, 1))[move_num % 2], ('D', 'L', 'W'))) / len(moves))
        for move in possible_moves
        }
    max_score = max(s.items(), key=itemgetter(1))[1]
    return tuple(m for m in possible_moves if s[m] == max_score)
