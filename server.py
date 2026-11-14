"""Tiny web server for the Tic-Tac-Toe agent. Python standard library only.

Run:   python3 server.py
Open:  http://localhost:8000

All game logic and AI decisions happen here in Python. The browser (HTML/CSS/JS)
only draws the board and sends clicks to the /api/play endpoint.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import game
from ai import choose_move, FULL_DEPTH

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")


class BadRequest(Exception):
    pass


def handle_play(data):
    """Apply the human's move (if any), then let the AI reply.

    Request:  {board: [9 cells], ai: "X"|"O", human_move: 0-8 or null,
               mode: "dfs"|"heuristic", depth: 1-9}
    """
    if not isinstance(data, dict):
        raise BadRequest("request body must be a JSON object.")

    board = data.get("board")
    ai_player = data.get("ai")
    human_move = data.get("human_move")
    mode = data.get("mode", "heuristic")
    depth = data.get("depth", FULL_DEPTH)

    if not (isinstance(board, list) and len(board) == 9
            and all(c in ("X", "O", " ") for c in board)):
        raise BadRequest("board must be a list of 9 cells: 'X', 'O' or ' '.")
    if ai_player not in ("X", "O"):
        raise BadRequest("ai must be 'X' or 'O'.")
    if mode not in ("dfs", "heuristic"):
        raise BadRequest("mode must be 'dfs' or 'heuristic'.")
    if not (type(depth) is int and 1 <= depth <= FULL_DEPTH):
        raise BadRequest("depth must be a whole number from 1 to 9.")
    if abs(board.count("X") - board.count("O")) > 1 or board.count("O") > board.count("X"):
        raise BadRequest("that board position is not reachable in a real game.")
    if game.status(board) != "playing":
        raise BadRequest("the game is already over.")

    human = game.opponent(ai_player)

    if human_move is not None:
        if game.next_player(board) != human:
            raise BadRequest("it is not the human's turn.")
        if not (type(human_move) is int and 0 <= human_move <= 8) or board[human_move] != " ":
            raise BadRequest("that square is not available.")
        board = game.play(board, human_move, human)

    ai_info = None
    if game.status(board) == "playing" and game.next_player(board) == ai_player:
        ai_info = choose_move(board, ai_player, mode, depth)
        board = game.play(board, ai_info["move"], ai_player)
        ai_info["scores"] = {str(k): v for k, v in ai_info["scores"].items()}

    line = game.winning_line(board)
    return {
        "board": board,
        "status": game.status(board),
        "line": list(line) if line else None,
        "ai": ai_info,
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, payload):
        self._send(code, json.dumps(payload).encode("utf-8"), "application/json")

    def do_GET(self):
        entry = STATIC_FILES.get(self.path.split("?")[0])
        if not entry:
            self._json(404, {"error": "not found"})
            return
        filename, content_type = entry
        with open(os.path.join(STATIC_DIR, filename), "rb") as f:
            self._send(200, f.read(), content_type)

    def do_POST(self):
        if self.path != "/api/play":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            self._json(200, handle_play(data))
        except BadRequest as e:
            self._json(400, {"error": str(e)})
        except (ValueError, TypeError):
            self._json(400, {"error": "request body must be valid JSON."})

    def log_message(self, fmt, *args):
        pass   # keep the terminal quiet


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    display_host = "localhost" if HOST in ("0.0.0.0", "::") else HOST
    print(f"Tic-Tac-Toe agent running at http://{display_host}:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
