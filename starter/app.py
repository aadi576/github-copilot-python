from flask import Flask, render_template, jsonify, request
import random
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Accept a difficulty name (easy/medium/hard). Default to 'medium'
    difficulty = request.args.get('difficulty', 'medium')
    if not isinstance(difficulty, str):
        difficulty = 'medium'
    difficulty = difficulty.lower()
    # Validate against sudoku_logic's difficulty map if available
    levels = getattr(sudoku_logic, 'DIFFICULTY_LEVELS', {})
    if difficulty not in levels:
        difficulty = 'medium'

    puzzle, solution = sudoku_logic.generate_puzzle(difficulty)
    # reset locked hints when starting a new game
    CURRENT['locked'] = []
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})


@app.route('/hint')
def hint():
    # Provide a single hint by filling one empty cell from the solution.
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400
    # Collect all empty cells and choose one at random so hints vary
    empties = [
        (i, j)
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
        if puzzle[i][j] == sudoku_logic.EMPTY
    ]
    if not empties:
        return jsonify({'error': 'No empty cells left'}), 400

    i, j = random.choice(empties)
    val = solution[i][j]
    puzzle[i][j] = val
    locked = CURRENT.setdefault('locked', [])
    if [i, j] not in locked:
        locked.append([i, j])
    return jsonify({'row': i, 'col': j, 'value': val, 'locked': True})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400
    board = data.get('board')
    if board is None:
        return jsonify({'error': 'Missing "board" in request'}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            # If board is malformed, this may raise; let that surface as a 500
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])

    # Puzzle is complete when there are no incorrect cells and no empties
    no_incorrect = len(incorrect) == 0
    all_filled = all(
        board[i][j] != sudoku_logic.EMPTY
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
    )
    complete = no_incorrect and all_filled

    return jsonify({'incorrect': incorrect, 'complete': complete})

if __name__ == '__main__':
    app.run(debug=True)