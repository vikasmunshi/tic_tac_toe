#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/game_graph.py
import atexit
import collections
import operator
import os.path
import pickle

from .user_types import Board, Cells, Game, TypeFuncBoard, TypeGraphNode, TypeGraphPath, TypeGraphPaths
from .util import cached

START = ()
END_D = 'D'
END_O = 'O'
END_X = 'X'

graph = collections.defaultdict(set)


@cached
def add_game_to_graph(game: Game) -> None:
    global graph
    graph[START].add(game.moves[0:1])
    for i in range(1, len(game.moves)):
        graph[game.moves[0:i]].add(game.moves[0:i + 1])
    graph[game.moves].add(game.result)


@cached
def dump_graph(cache_file: str) -> None:
    with open(cache_file, 'wb') as outfile:
        pickle.dump(graph, outfile)


@cached
def find_all_paths(start: TypeGraphNode, end: TypeGraphNode) -> TypeGraphPaths:
    def _find_all_paths(s: TypeGraphNode, e: TypeGraphNode, path: TypeGraphPath) -> TypeGraphPaths:
        path += (s,)
        if s == e:
            return path,
        if s not in graph:
            return ()
        paths = ()
        for node in graph[s]:
            if node not in path:
                new_paths = _find_all_paths(node, e, path)
                for new_path in new_paths:
                    paths += (new_path,)
        return paths

    return _find_all_paths(start, end, ())


@cached
def find_path(start: TypeGraphNode, end: TypeGraphNode) -> TypeGraphPath:
    def _find_path(s: TypeGraphNode, e: TypeGraphNode, path: TypeGraphPath) -> TypeGraphPath:
        path += (s,)
        if s == e:
            return path
        if s not in graph:
            return ()
        for node in graph[s]:
            if node not in path:
                new_path = _find_path(node, e, path)
                if new_path: return new_path
        return ()

    return _find_path(start, end, ())


@cached
def find_shortest_path(start: TypeGraphNode, end: TypeGraphNode) -> TypeGraphPath:
    def _find_shortest_path(s: TypeGraphNode, e: TypeGraphNode, path: TypeGraphPath) -> TypeGraphPath:
        path += (s,)
        if s == e:
            return path
        if s not in graph:
            return ()
        shortest = ()
        for node in graph[s]:
            if node not in path:
                new_path = _find_shortest_path(node, e, path)
                if new_path:
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path
        return shortest

    return _find_shortest_path(start, end, ())


@cached
def load_graph(graph_name: str, size: int) -> bool:
    global graph
    cache_file = os.path.abspath(os.path.splitext(graph_name)[0] + '.graph_{0}x{0}.pickle'.format(size))
    atexit.register(dump_graph, cache_file=cache_file)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as infile:
                graph = pickle.load(infile)
        except (EOFError, FileNotFoundError, IOError, ModuleNotFoundError):
            return True
        else:
            return False

    return True


def remembered_in_graph(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        result = func(board)
        if result:
            add_game_to_graph(Game(moves=board.moves, result=result))
        return result

    return f


@cached
def suggest_moves_graph(board: Board, possible_moves: Cells) -> Cells:
    if len(possible_moves) > 1:
        end_win = (END_X, END_O)[len(board.moves) % 2]
        end_loss = [e for e in (END_X, END_O) if e != end_win][0]
        moves = {move:
                     {
                         'D': len(find_all_paths(board.moves + (move,), END_D)),
                         'L': len(find_all_paths(board.moves + (move,), end_loss)),
                         'W': len(find_all_paths(board.moves + (move,), end_win)),

                     } for move in possible_moves
                 }

        wins = tuple(move for move in possible_moves
                     if moves[move]['W'] > 0 and moves[move]['L'] == 0 and moves[move]['D'] == 0)
        if wins:
            return wins

        no_loss = tuple(move for move in possible_moves if moves[move]['L'] == 0)
        if no_loss:
            return no_loss

        weights = zip(((0, -2, 1), (1, -3, 1))[len(board.moves) % 2], ('D', 'L', 'W'))
        scores = {move: sum(wt * moves[move][b] for wt, b in weights) for move in possible_moves}
        max_score = max(scores.items(), key=operator.itemgetter(1))[1]
        return tuple(m for m in possible_moves if scores[m] == max_score)

    return possible_moves
