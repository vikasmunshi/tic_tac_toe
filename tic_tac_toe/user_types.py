#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/types.py
import collections
import typing

Board = collections.namedtuple('Board', ('size', 'moves'))
Cell = collections.namedtuple('Cell', ('row_id', 'col_id'))
Cell.__repr__ = lambda self: 'c{}{}'.format(self.row_id, self.col_id)
Cells = typing.Tuple[Cell, ...]
Game = collections.namedtuple('Game', ['moves', 'result'])
Games = typing.Tuple[Game, ...]
Lines = typing.Tuple[Cells, ...]
Moves = Cells
Player = collections.namedtuple('Player', ('name', 'strategy'))
Player.__repr__ = lambda self: self.name
Players = typing.Tuple[Player, ...]
Score = collections.namedtuple('Score', ('player', 'points', 'wins', 'draws', 'losses', 'games', 'penalties'))
Scores = typing.Tuple[Score, ...]
TypeFunc = typing.Callable[[tuple, dict], str]
TypeFuncBoard = typing.Callable[[Board], str]
TypeFuncGame = typing.Callable[[int, Player, Player], str]
TypeGraphNode = typing.Union[Moves, str]
TypeGraphPath = typing.Tuple[TypeGraphNode, ...]
TypeGraphPaths = typing.Tuple[TypeGraphPath, ...]
TypeTupleOfTuples = typing.Union[typing.Tuple[typing.Tuple, ...],
                                 typing.Generator[typing.Tuple[typing.Tuple, ...], None, None]]
