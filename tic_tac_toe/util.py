#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
import collections
import functools
import io
import itertools
import random
import sys
import typing

from .types import Cell, Cells, TypeFunc, TypeTupleOfTuples

Counter = collections.Counter
cached = functools.lru_cache(maxsize=None, typed=False)


def count_sub_items(l: TypeTupleOfTuples) -> dict:
    return Counter((i for s in l for i in s))


def flatten(l: TypeTupleOfTuples) -> ():
    return tuple([i for s in l for i in s])


def get_permutations(iterable: typing.Iterable) -> typing.Iterable:
    return itertools.permutations(iterable)


def logged(func: TypeFunc, log_file: io.TextIOBase = sys.stderr) -> TypeFunc:
    def f(*args, **kwargs) -> str:
        r = func(*args, **kwargs)
        if func.__name__ == '<lambda>':
            print('msg ->', r, file=log_file)
        else:
            print('{} ({}) -> {}'.format(func.__name__, ', '.join(str(arg) for arg in args), r), file=log_file)
        return r

    return f


def printed(func: TypeFunc, print_file: io.TextIOBase = sys.stderr) -> TypeFunc:
    def f(*args, **kwargs) -> str:
        r = func(*args, **kwargs)
        print(r, file=print_file)
        return r

    return f


def select_random_cell(cells: Cells) -> Cell:
    return random.choice(cells) if cells else None
