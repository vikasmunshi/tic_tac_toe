#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/core.py
from .game_graph import load_graph, add_game_to_graph
from .game_memory import load_memory, add_game_to_memory, remembered_in_memory
from .user_types import Board, Cell, Cells, Game, Lines, Player
from .util import cached, get_permutations, printed, select_random_cell
from .visualize import show_board, show_game


@cached
def add_move_to_board(board: Board, move: Cell) -> Board:
    return Board(board.size, board.moves + (move,))


@cached
def board_is_full(board: Board) -> bool:
    return not get_possible_moves(board)


@cached
def create_empty_board(size: int) -> Board:
    return Board(size, ())


@show_board
@cached
@remembered_in_memory
@remembered_in_memory
def check_winner(board: Board) -> str:
    return ('O', 'X')[len(board.moves) % 2] if last_move_has_won(board) else 'D' if board_is_full(board) else ''


@cached
def get_cells(board: Board) -> Cells:
    return tuple(Cell(row_id, col_id) for row_id in range(board.size) for col_id in range(board.size))


@cached
def get_columns(board: Board) -> Lines:
    return tuple(tuple(Cell(row_id, col_id) for row_id in range(board.size)) for col_id in range(board.size))


@cached
def get_diagonals(board: Board) -> Lines:
    return tuple(Cell(n, n) for n in range(board.size)), tuple(Cell(n, board.size - 1 - n) for n in range(board.size))


@cached
def get_lines(board: Board) -> Lines:
    return get_rows(board) + get_columns(board) + get_diagonals(board)


@cached
def get_possible_moves(board: Board) -> Cells:
    return tuple(cell for cell in get_cells(board) if cell not in board.moves)


@cached
def get_moves_of_last_player(board: Board) -> Cells:
    return board.moves[1 - len(board.moves) % 2::2]


@cached
def get_rows(board: Board) -> Lines:
    return tuple(tuple(Cell(row_id, col_id) for col_id in range(board.size)) for row_id in range(board.size))


@cached
def last_move_has_won(board: Board) -> bool:
    return any([all([cell in get_moves_of_last_player(board) for cell in line]) for line in get_lines(board)])


def play(board: Board, one: Player, two: Player) -> str:
    try:
        move = one.strategy(board)
    except SystemExit:
        printed(lambda: 'bad bad {} tried to exit()!'.format(one.name))()
        return 'I.{}'.format(one.name)
    except Exception as e:
        printed(lambda: repr(e))()
        return 'I.{}'.format(one.name)
    if move not in get_possible_moves(board):
        return 'I.{}'.format(one.name)
    return check_winner(add_move_to_board(board, move)) or play(add_move_to_board(board, move), two, one)


@show_game
def play_game(size: int, one: Player, two: Player) -> str:
    return {
        'X': one.name,
        'O': two.name,
        'D': 'D',
        'I.{}'.format(one.name): 'I.{}'.format(one.name),
        'I.{}'.format(two.name): 'I.{}'.format(two.name)

    }[play(create_empty_board(size), one, two)]


def play_game_set(size: int, one: Player, two: Player) -> (str, str):
    return play_game(size, one, two), play_game(size, two, one)


@cached
def re_memorize_games(size: int) -> None:
    if (load_memory(__file__, size) or load_graph(__file__, size)) and size < 4:
        for game in (reduce_board(Board(size, moves))
                     for moves in get_permutations(get_cells(Board(size=size, moves=())))):
            add_game_to_memory(game)
            add_game_to_graph(game)


@cached
def reduce_board(board: Board) -> Game:
    for subset_moves in (board.moves[0:n] for n in range(2 * board.size - 1, board.size * board.size + 1)):
        if last_move_has_won(Board(board.size, subset_moves)):
            return Game(moves=subset_moves, result=('O', 'X')[len(subset_moves) % 2])
    return Game(moves=board.moves, result='D')


def strategy(board: Board) -> Cell:
    return select_random_cell(get_possible_moves(board))
