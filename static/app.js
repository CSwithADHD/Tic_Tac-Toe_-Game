// The browser only draws the board and sends clicks to the Python server.
// All rules and all AI decisions come back from /api/play.

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const reasonEl = document.getElementById("reason");
const nodesEl = document.getElementById("nodes");
const timeEl = document.getElementById("time");
const miniEl = document.getElementById("mini");

const score = { you: 0, draw: 0, ai: 0 };
let board, aiSymbol, humanSymbol, over, busy, winLine, gameId = 0;

const X_SVG = '<svg viewBox="0 0 100 100" aria-hidden="true"><path class="mark-x draw" pathLength="1" d="M12 12 L88 88 M88 12 L12 88"/></svg>';
const O_SVG = '<svg viewBox="0 0 100 100" aria-hidden="true"><circle class="mark-o draw" pathLength="1" cx="50" cy="50" r="38"/></svg>';

const setting = (name) => document.querySelector(`input[name="${name}"]:checked`).value;

function render() {
  boardEl.innerHTML = "";
  board.forEach((mark, i) => {
    const cell = document.createElement("button");
    cell.type = "button";
    cell.className = "cell" + (winLine && winLine.includes(i) ? " win" : "");
    cell.setAttribute("role", "gridcell");
    const row = Math.floor(i / 3) + 1, col = (i % 3) + 1;
    cell.setAttribute("aria-label", `Row ${row}, column ${col}: ${mark === " " ? "empty" : mark}`);
    cell.disabled = over || busy || mark !== " ";
    if (mark === "X") cell.innerHTML = X_SVG;
    if (mark === "O") cell.innerHTML = O_SVG;
    cell.addEventListener("click", () => humanMove(i));
    boardEl.appendChild(cell);
  });
}

async function callServer(humanMoveIndex) {
  const res = await fetch("/api/play", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      board, ai: aiSymbol, human_move: humanMoveIndex,
      mode: setting("mode"), depth: Number(setting("depth")),
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Server error");
  return data;
}

function applyResult(data) {
  board = data.board;
  winLine = data.line;
  if (data.ai) showAiInfo(data.ai);
  if (data.status !== "playing") finish(data.status);
  else statusEl.textContent = "Your turn.";
}

function finish(st) {
  over = true;
  if (st === "draw") { score.draw++; statusEl.textContent = "It's a draw."; }
  else if (st === aiSymbol) { score.ai++; statusEl.textContent = "The AI wins."; }
  else { score.you++; statusEl.textContent = "You win!"; }
  document.getElementById("score-you").textContent = score.you;
  document.getElementById("score-draw").textContent = score.draw;
  document.getElementById("score-ai").textContent = score.ai;
}

function showAiInfo(info) {
  const reasons = {
    win: "It could finish three in a row, so it took the win.",
    block: "You were about to win, so it blocked that square.",
    search: "No immediate win or block, so it searched the game tree and picked the best score.",
  };
  reasonEl.textContent = reasons[info.reason];
  nodesEl.textContent = info.nodes.toLocaleString();
  timeEl.textContent = info.time_ms;
  renderMini(info);
}

function renderMini(info) {
  // Show the board as it was before the AI moved, with each empty square's score.
  miniEl.innerHTML = "";
  for (let i = 0; i < 9; i++) {
    const d = document.createElement("div");
    const before = i === info.move ? " " : board[i];
    if (info.scores[i] !== undefined) {
      d.textContent = info.scores[i];
      if (i === info.move) d.className = "chosen";
    } else if (i === info.move) {
      d.textContent = aiSymbol;
      d.className = "chosen";
    } else if (before !== " ") {
      d.textContent = before;
      d.className = "taken " + before.toLowerCase();
    }
    miniEl.appendChild(d);
  }
}

async function humanMove(i) {
  if (over || busy || board[i] !== " ") return;
  const myGame = gameId;
  busy = true;
  board[i] = humanSymbol;          // show the click straight away
  statusEl.textContent = "AI is thinking…";
  render();
  board[i] = " ";                  // the server returns the real board
  try {
    const data = await callServer(i);
    if (myGame !== gameId) return; // a new game started meanwhile
    busy = false;
    applyResult(data);
  } catch (err) {
    busy = false;
    statusEl.textContent = err.message;
  }
  render();
}

async function newGame() {
  gameId++;
  const myGame = gameId;
  aiSymbol = setting("first") === "ai" ? "X" : "O";
  humanSymbol = aiSymbol === "X" ? "O" : "X";
  board = Array(9).fill(" ");
  over = false; busy = false; winLine = null;
  miniEl.innerHTML = "";
  reasonEl.textContent = "The AI has not moved yet.";
  nodesEl.textContent = timeEl.textContent = "–";

  if (aiSymbol === "X") {          // the AI opens
    busy = true;
    statusEl.textContent = "AI is thinking…";
    render();
    try {
      const data = await callServer(null);
      if (myGame !== gameId) return;
      busy = false;
      applyResult(data);
    } catch (err) {
      busy = false;
      statusEl.textContent = err.message;
    }
  } else {
    statusEl.textContent = "Your turn. You are X.";
  }
  render();
}

document.getElementById("new-game").addEventListener("click", newGame);
document.querySelectorAll('input[name="first"]').forEach((r) => r.addEventListener("change", newGame));
newGame();
