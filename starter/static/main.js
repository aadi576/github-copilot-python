// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintCount = 0;
let gameCompleted = false;

// Format elapsed seconds for the timer and scoreboard.
function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function updateTimer() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

// Load, sort, and display the persistent top-ten scoreboard.
function renderScores() {
  let scores = [];
  try {
    scores = JSON.parse(localStorage.getItem('sudokuScores')) || [];
  } catch (error) {
    scores = [];
  }
  scores.sort((first, second) => first.time - second.time);
  const scoreList = document.getElementById('score-list');
  scoreList.innerHTML = '';
  scores.slice(0, 10).forEach((score) => {
    const item = document.createElement('li');
    item.innerText = `${score.name} - ${formatTime(score.time)} - ${score.difficulty} - ${score.hints} hint(s)`;
    scoreList.appendChild(item);
  });
}

// Prompt for a completed player's name and persist their score.
function saveScore() {
  const name = prompt('Puzzle complete! Enter your name:');
  if (!name || !name.trim()) return;
  let scores = [];
  try {
    scores = JSON.parse(localStorage.getItem('sudokuScores')) || [];
  } catch (error) {
    scores = [];
  }
  scores.push({
    name: name.trim(),
    time: elapsedSeconds,
    difficulty: document.getElementById('difficulty').value,
    hints: hintCount
  });
  scores.sort((first, second) => first.time - second.time);
  try {
    localStorage.setItem('sudokuScores', JSON.stringify(scores.slice(0, 10)));
  } catch (error) {
    document.getElementById('message').innerText = 'Your score could not be saved.';
    return;
  }
  renderScores();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  hintCount = 0;
  gameCompleted = false;
  startTimer();
}

async function getHint() {
  const msg = document.getElementById('message');
  const res = await fetch('/hint');
  const data = await res.json();
  if (!res.ok || data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error || 'Unable to get a hint.';
    return;
  }

  const index = data.row * SIZE + data.col;
  const input = document.getElementById('sudoku-board').getElementsByTagName('input')[index];
  if (input) {
    input.value = data.value;
    input.disabled = true;
    input.className = 'sudoku-cell hint-cell';
    hintCount += 1;
  }
  msg.style.color = '';
  msg.innerText = 'A hint has been added.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (data.complete) {
    stopTimer();
    if (!gameCompleted) {
      gameCompleted = true;
      saveScore();
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('dark-mode').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
  });
  renderScores();
  // initialize
  newGame();
});