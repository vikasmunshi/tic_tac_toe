#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
import os.path
import pickle

from .types import Board, Cell, Cells, Game, Moves, TypeFuncBoard

cache = {}


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
    return cache.get(moves, {})


def remember(moves: Cells, next_move: Cell, winner: str) -> None:
    global cache
    if moves not in cache:
        cache[moves] = {}
    if next_move not in cache[moves]:
        cache[moves][next_move] = {'W': 0, 'D': 0, 'L': 0, 'S': 0}
    move_num_2 = len(moves) % 2
    bucket = 'D' if winner == 'D' else 'W' if winner == ('X', 'O')[move_num_2] else 'L'
    cache[moves][next_move][bucket] += 1
    cache[moves][next_move]['S'] = score_moves(cache[moves][next_move], move_num_2)


def remember_game(game: Game) -> None:
    for moves, next_move, winner in ((game.moves[:i], game.moves[i], game.result) for i in range(0, len(game.moves))):
        remember(moves, next_move, winner)


def remembered(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            remember_game(Game(moves=board.moves, result=result))
        return result

    return f


def score_moves(score: dict, move_num_2: int) -> int:
    return int(100 * (score['W'] + (score['D'] * move_num_2) - score['L']) / (score['W'] + score['D'] + score['L']))
