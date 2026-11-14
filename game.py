"""Board and game rules for 3x3 Tic-Tac-Toe.

The board is a list of 9 cells, indexed 0-8 from top-left, row by row:

    0 | 1 | 2
    3 | 4 | 5
    6 | 7 | 8

Each cell is "X", "O" or " " (empty).
"""

EMPTY = " "

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]


def new_board():
    return [EMPTY] * 9


def opponent(player):
    return "O" if player == "X" else "X"


def winning_line(board):
    """Return the 3 cell indices of a completed line, or None."""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None


def winner(board):
    """Return "X" or "O" if someone has won, otherwise None."""
    line = winning_line(board)
    return board[line[0]] if line else None


def legal_moves(board):
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def is_full(board):
    return EMPTY not in board


def status(board):
    """Return "X", "O", "draw" or "playing"."""
    w = winner(board)
    if w:
        return w
    return "draw" if is_full(board) else "playing"


def next_player(board):
    """X always moves first, so X is next whenever the counts are equal."""
    return "X" if board.count("X") == board.count("O") else "O"


def play(board, move, player):
    """Return a new board with `player` placed on `move`."""
    new = board[:]
    new[move] = player
    return new
