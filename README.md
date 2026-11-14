# Intelligent Tic-Tac-Toe Game Agent (CSL-325 AI Lab)

A web-based Tic-Tac-Toe game where you play against an AI agent. The page is plain
HTML + CSS + a little JavaScript. All game rules and AI logic are written in Python.
Python standard library only; no pip install, works offline.

## Run it

    python3 server.py

Then open http://localhost:8000 in your browser. (Set `PORT=9000` to change the port.)

### Open it on other devices on the same Wi-Fi

1. Start the server on the computer hosting the game:

       py -3 server.py

2. Find that computer's local IPv4 address with `ipconfig` (for example,
   `192.168.1.25`).
3. On another device connected to the same Wi-Fi, open
   `http://192.168.1.25:8000`.
4. If Windows Firewall prompts you, allow Python on **Private networks**. If it
   still cannot connect, add an inbound TCP rule for port 8000.

The server listens on all network interfaces by default. To restrict it back to
the local computer, run `set HOST=127.0.0.1` before starting it.

### Deploy it publicly

#### Vercel

This repository includes a Vercel serverless entry point in `api/index.py` and
the routing configuration in `vercel.json`.

1. Push the project to GitHub.
2. In Vercel, choose **Add New Project**, import the repository, and click
   **Deploy**.
3. Leave the framework preset and build command at their defaults. No
   environment variables are required.

Vercel will serve the page over HTTPS and run `/api/play` as a Python
serverless function, so it works from any device with internet access. You can
also deploy from the project directory with the Vercel CLI:

       npx vercel

The production URL printed by Vercel is the link to share.

#### Other Python hosts

The original long-running server can also run on hosts that support Python web
services, such as Render, Railway, or Fly.io. Configure:

- **Build command:** none
- **Start command:** `python server.py`
- **Environment:** `HOST=0.0.0.0`
- **Port:** use the platform-provided `PORT` environment variable

The server already reads `HOST` and `PORT`, and the browser uses a relative
`/api/play` URL, so the frontend and API work from the same public address.
For a public deployment, use HTTPS and do not expose the development server
directly to untrusted users without adding authentication/rate limiting.

## Files

| File | What it does |
| --- | --- |
| `game.py` | Board, turn handling, win / draw detection |
| `ai.py` | The agent: win/block rules, recursive DFS game-tree search, heuristic evaluation |
| `server.py` | Small web server (`http.server`) with one endpoint, `/api/play` |
| `static/index.html`, `style.css`, `app.js` | The web page |
| `evaluate.py` | Plays 100+ automated games and reports win/draw/loss and nodes explored |
| `tests.py` | Checks the acceptance criteria from the proposal |

## How the AI decides

1. Can I win now? Take it.
2. Is the opponent about to win? Block it.
3. Otherwise search the game tree with depth-first search and pick the best score.

**Heuristic** (`ai.heuristic`): +10 for a win, -10 for a loss. For an undecided board,
look at the 8 winning lines. A line holding only my marks is worth +1 (one mark) or
+3 (two marks); a line holding only the opponent's marks is worth the same, negated;
mixed lines are dead (0).

**Two search modes** (to compare "with and without the heuristic"):
- `dfs`: plain DFS, no heuristic, no pruning.
- `heuristic`: DFS that scores undecided positions with the heuristic, and visits the
  most promising moves first so alpha-beta pruning can skip whole branches.

## Check the results

    python3 tests.py          # takes wins, blocks losses, never loses
    python3 evaluate.py 100   # 100 games per opponent per mode, writes results.json

Sample output (100 games each, AI plays X in half and O in half):

| mode | opponent | W | D | L | nodes / AI move |
| --- | --- | --- | --- | --- | --- |
| dfs | random | 96 | 4 | 0 | 96,074 |
| dfs | human-like | 41 | 59 | 0 | 75,058 |
| dfs | perfect | 0 | 100 | 0 | 68,031 |
| heuristic | random | 96 | 4 | 0 | 912 |
| heuristic | human-like | 41 | 59 | 0 | 723 |
| heuristic | perfect | 0 | 100 | 0 | 664 |

Same results (never loses), about 100x fewer positions searched with the heuristic.
