"""Evaluate the agent: win/draw/loss rate and nodes explored, with and without the heuristic.

Run:  python3 evaluate.py            (100 games per opponent per mode)
      python3 evaluate.py 200        (200 games)

Opponents
  random  - picks any empty square
  human   - "human-like": takes a win, blocks a loss, otherwise picks randomly
  perfect - plays the best possible game (full-depth heuristic search)

The AI plays X (first) in half the games and O (second) in the other half.
Results are also written to results.json.
"""

import json
import os
import random
import sys

import game
from ai import choose_move, FULL_DEPTH, _finishing_move

_cache = {}
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def ai_move(board, me, mode):
    """choose_move with a cache. The search is deterministic, so a repeated position
    would explore the same nodes again; we reuse the answer but still count its cost."""
    key = (tuple(board), me, mode)
    if key not in _cache:
        _cache[key] = choose_move(board, me, mode, FULL_DEPTH)
    return _cache[key]


def opponent_move(kind, board, me, rng):
    moves = game.legal_moves(board)
    if kind == "random":
        return rng.choice(moves)
    if kind == "human":
        for who in (me, game.opponent(me)):
            m = _finishing_move(board, who)
            if m is not None:
                return m
        return rng.choice(moves)
    return ai_move(board, me, "heuristic")["move"]       # "perfect"


def play_game(mode, kind, ai_symbol, rng):
    board = game.new_board()
    nodes, ai_moves = 0, 0
    while game.status(board) == "playing":
        turn = game.next_player(board)
        if turn == ai_symbol:
            info = ai_move(board, turn, mode)
            nodes += info["nodes"]
            ai_moves += 1
            board = game.play(board, info["move"], turn)
        else:
            board = game.play(board, opponent_move(kind, board, turn, rng), turn)
    st = game.status(board)
    outcome = "draw" if st == "draw" else ("win" if st == ai_symbol else "loss")
    return outcome, nodes, ai_moves


def run(n_games):
    results = {}
    for mode in ("dfs", "heuristic"):
        for kind in ("random", "human", "perfect"):
            rng = random.Random(42)
            tally = {"win": 0, "draw": 0, "loss": 0}
            nodes = moves = 0
            for g in range(n_games):
                outcome, n, m = play_game(mode, kind, "X" if g % 2 == 0 else "O", rng)
                tally[outcome] += 1
                nodes += n
                moves += m
            results[f"{mode}/{kind}"] = {
                **tally, "games": n_games,
                "nodes_total": nodes,
                "nodes_per_ai_move": round(nodes / moves, 1),
            }
    return results


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    res = run(n)
    print(f"\n{n} games per row. The AI plays X in half the games and O in the other half.\n")
    print(f"{'search mode':<12}{'opponent':<10}{'wins':>6}{'draws':>7}{'losses':>8}{'nodes/AI move':>16}")
    for key, r in res.items():
        mode, kind = key.split("/")
        print(f"{mode:<12}{kind:<10}{r['win']:>6}{r['draw']:>7}{r['loss']:>8}{r['nodes_per_ai_move']:>16}")
    with open(RESULTS_PATH, "w") as f:
        json.dump(res, f, indent=2)
    print("\nSaved results.json")
