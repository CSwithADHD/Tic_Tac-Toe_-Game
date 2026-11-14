"""The Tic-Tac-Toe agent: depth-first game-tree search + heuristic evaluation.

Decision order for every AI move
--------------------------------
1. If the AI can win right now, take the win.
2. Otherwise, if the opponent threatens to win next turn, block it.
3. Otherwise, search the game tree with recursive DFS and pick the best-scored move.

Two search modes are provided so they can be compared (see evaluate.py):

* "dfs"       - plain depth-first search. No heuristic, no pruning. Positions that
                are still undecided at the depth limit are scored 0.
* "heuristic" - the same DFS, but
                  (a) undecided positions at the depth limit are scored by the
                      heuristic evaluation function,
                  (b) child moves are visited best-first according to that
                      heuristic, which lets alpha-beta pruning cut off branches.

Scores are always from the point of view of the AI player ("me").
"""

import time

from game import WIN_LINES, EMPTY, opponent, winner, legal_moves, play

WIN_SCORE = 10          # a won position is worth at least +10, a lost one at most -10
FULL_DEPTH = 9          # a Tic-Tac-Toe game has at most 9 moves

# Tie-break order when several moves have the same score: centre, corners, edges.
PREFERRED_ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]


# --------------------------------------------------------------------------- #
# Heuristic evaluation
# --------------------------------------------------------------------------- #
def heuristic(board, me):
    """Score a board from `me`'s point of view.

    * +10 if `me` has won, -10 if the opponent has won.
    * Otherwise look at the 8 winning lines. A line that only contains my marks is
      "open" for me and is worth 1 point (one mark) or 3 points (two marks).
      A line that only contains the opponent's marks is worth the same, negated.
      Lines holding both players' marks are dead and score 0.
    The result of an undecided board is clamped to -9..+9 so it can never beat a
    real win or loss.
    """
    opp = opponent(me)
    w = winner(board)
    if w == me:
        return WIN_SCORE
    if w == opp:
        return -WIN_SCORE

    score = 0
    for line in WIN_LINES:
        marks = [board[i] for i in line]
        mine, theirs = marks.count(me), marks.count(opp)
        if theirs == 0 and mine > 0:
            score += 1 if mine == 1 else 3
        elif mine == 0 and theirs > 0:
            score -= 1 if theirs == 1 else 3
    return max(-9, min(9, score))


# --------------------------------------------------------------------------- #
# Depth-first game-tree search
# --------------------------------------------------------------------------- #
class Counter:
    """Counts how many tree nodes (board positions) the search visits."""
    def __init__(self):
        self.nodes = 0


def dfs(board, to_move, me, depth, alpha, beta, counter, use_heuristic):
    """Recursive DFS. Returns the score of `board` for `me`.

    `depth` is how many more plies we may look ahead. When use_heuristic is False
    alpha/beta are ignored (no pruning) and the search is plain DFS.
    """
    counter.nodes += 1

    w = winner(board)
    if w:
        # Faster wins score higher, slower losses score higher (more depth left = sooner).
        return (WIN_SCORE + depth) if w == me else -(WIN_SCORE + depth)

    moves = legal_moves(board)
    if not moves:
        return 0                                        # draw
    if depth == 0:
        return heuristic(board, me) if use_heuristic else 0

    maximizing = (to_move == me)
    nxt = opponent(to_move)

    if use_heuristic:
        # Best-first: look at the children the heuristic likes most first.
        moves.sort(
            key=lambda m: heuristic(play(board, m, to_move), me),
            reverse=maximizing,
        )

    best = -999 if maximizing else 999
    for m in moves:
        score = dfs(play(board, m, to_move), nxt, me, depth - 1,
                    alpha, beta, counter, use_heuristic)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if use_heuristic and alpha >= beta:
            break                                       # prune the remaining children
    return best


# --------------------------------------------------------------------------- #
# Move selection
# --------------------------------------------------------------------------- #
def _finishing_move(board, player):
    """A move that gives `player` three in a row immediately, or None."""
    for m in legal_moves(board):
        if winner(play(board, m, player)) == player:
            return m
    return None


def choose_move(board, me, mode="heuristic", depth=FULL_DEPTH):
    """Pick a move for `me`. Returns a dict describing the decision."""
    start = time.perf_counter()
    counter = Counter()

    def result(move, reason, scores=None):
        return {
            "move": move,
            "reason": reason,                           # "win", "block" or "search"
            "nodes": counter.nodes,
            "time_ms": round((time.perf_counter() - start) * 1000, 2),
            "scores": scores or {},
        }

    # 1. Take an immediate win.
    m = _finishing_move(board, me)
    if m is not None:
        return result(m, "win")

    # 2. Block the opponent's immediate win.
    m = _finishing_move(board, opponent(me))
    if m is not None:
        return result(m, "block")

    # 3. Search the game tree.
    use_heuristic = (mode == "heuristic")
    scores = {}
    for m in legal_moves(board):
        scores[m] = dfs(play(board, m, me), opponent(me), me, depth - 1,
                        -999, 999, counter, use_heuristic)

    best_score = max(scores.values())
    best = next(m for m in PREFERRED_ORDER if m in scores and scores[m] == best_score)
    return result(best, "search", scores)
