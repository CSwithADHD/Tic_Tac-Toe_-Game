"""Checks the proposal's acceptance criteria. Run:  python3 tests.py

1. The AI always takes an immediate win.
2. The AI always blocks an immediate loss (when it cannot win itself).
3. The AI never loses: every possible opponent reply is tried, as X and as O.
"""

import game
from ai import choose_move, _finishing_move, FULL_DEPTH

cache = {}


def ai(board, me, mode="heuristic"):
    key = (tuple(board), me, mode)
    if key not in cache:
        cache[key] = choose_move(board, me, mode, FULL_DEPTH)
    return cache[key]


def all_positions(board, seen):
    """Every position reachable in a real game."""
    key = tuple(board)
    if key in seen:
        return
    seen.add(key)
    if game.status(board) != "playing":
        return
    turn = game.next_player(board)
    for m in game.legal_moves(board):
        all_positions(game.play(board, m, turn), seen)


def test_win_and_block():
    positions = set()
    all_positions(game.new_board(), positions)
    wins = blocks = 0
    for pos in positions:
        board = list(pos)
        if game.status(board) != "playing":
            continue
        me = game.next_player(board)
        for mode in ("dfs", "heuristic"):
            move = ai(board, me, mode)["move"]
            win = _finishing_move(board, me)
            if win is not None:
                assert game.winner(game.play(board, move, me)) == me, (board, mode)
                wins += 1
            else:
                threat = _finishing_move(board, game.opponent(me))
                if threat is not None:
                    assert move == threat, (board, mode)
                    blocks += 1
    print(f"ok  takes the win ({wins} positions) and blocks the loss ({blocks} positions)")


def never_loses(board, me, mode):
    """Try every opponent reply to the AI's choices; return False if the AI can lose."""
    st = game.status(board)
    if st != "playing":
        return st != game.opponent(me)
    turn = game.next_player(board)
    if turn == me:
        return never_loses(game.play(board, ai(board, me, mode)["move"], me), me, mode)
    return all(never_loses(game.play(board, m, turn), me, mode)
               for m in game.legal_moves(board))


def test_never_loses():
    for mode in ("dfs", "heuristic"):
        for me in ("X", "O"):
            assert never_loses(game.new_board(), me, mode), (mode, me)
    print("ok  never loses (every opponent reply, both modes, as X and as O)")


if __name__ == "__main__":
    test_win_and_block()
    test_never_loses()
    print("All checks passed.")
