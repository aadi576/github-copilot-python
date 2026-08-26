# Sudoku Project — Copilot Instructions

## Project Overview
A Flask-based Sudoku game refactored from legacy code. Puzzle generation
and validation logic live in Python; the board UI, timer, hints, and
scoreboard are plain JavaScript and CSS. There is no frontend framework.

## Architecture — keep this separation
- `starter/app.py` — Flask routes ONLY. Routes should validate input,
  call into `sudoku_logic.py`, and return JSON. No puzzle-generation or
  solving logic belongs here.
- `starter/sudoku_logic.py` — all puzzle logic: board creation, solving,
  uniqueness checking, difficulty-to-clue-count mapping. Do not duplicate
  backtracking logic across functions; reuse `is_safe`/`solve_board`
  where possible.
- `starter/static/main.js` — all client-side board rendering, timer,
  hint/check wiring, dark mode, and the localStorage scoreboard.
- `starter/static/styles.css` — plain CSS only, no framework. Keep
  light/dark mode rules grouped under `body.dark-mode` selectors.
- `starter/templates/index.html` — structure only; no inline styles or
  inline scripts beyond what's already there.

## Non-negotiable game rules — do not break these
- Every generated puzzle must have exactly one solution. Any change to
  `remove_cells` or puzzle generation must preserve the uniqueness check
  (`count_solutions(board, limit=2) == 1`) before a cell is permanently
  removed.
- Difficulty levels (`easy`, `medium`, `hard`) map to fixed clue counts in
  `DIFFICULTY_LEVELS`. Don't hardcode clue counts elsewhere.
- Prefilled/locked cells (including hint cells) must never become
  editable after being set.

## Code Style
- Keep it clean and simple. Prefer straightforward, readable code over
  clever one-liners.
- Minimal dependencies — don't add a new library if the standard library,
  Flask, or plain JS/CSS can do the job.
- snake_case for Python, camelCase for JavaScript.
- Small, focused functions — one responsibility each.

## Error Handling (required, not optional)
- Every Flask route must validate its input before using it. Never assume
  request JSON has the expected shape or types — check explicitly and
  return a clear 4xx JSON error (e.g. `{"error": "..."}`) for anything
  malformed, rather than letting an exception surface as a 500.
- Frontend fetch calls should handle non-OK responses and network/storage
  failures (e.g. `localStorage` write failures) with a visible message to
  the user, not a silent failure.

## Testing
- Use pytest for backend tests, run from the `starter` directory.
- After any change to `sudoku_logic.py` or `app.py`, run `pytest` and add
  a focused test for the new/changed behavior (e.g. a malformed `/check`
  request should have a test asserting a 400 response).
- Verify uniqueness-checking performance manually if touching
  `remove_cells` — puzzle generation should stay well under a few seconds
  even for "hard" difficulty.

## Working with Copilot Suggestions
- Don't accept a suggestion blindly. If it introduces a new dependency,
  significantly changes structure, or skips validation, ask Copilot to
  explain or revise before accepting.
- If a suggestion only covers the happy path (e.g. assumes well-formed
  input, ignores an edge case), explicitly ask for the edge case to be
  handled — don't accept partial correctness as done.