import copy
import random

SIZE = 9
EMPTY = 0

# Typical clue counts by difficulty (number of filled cells)
DIFFICULTY_LEVELS = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def solve_board(board):
    """Return a solved copy of `board` if solvable, otherwise None.

    This reuses the existing `fill_board` backtracking routine by operating
    on a deep copy so the original is not mutated.
    """
    b = deep_copy(board)
    if fill_board(b):
        return b
    return None


def count_solutions(board, limit=2):
    """Count up to `limit` solutions for `board` and return the count.

    The function stops early when `limit` is reached for performance.
    """
    b = deep_copy(board)
    count = 0

    def backtrack():
        nonlocal count
        # Early exit
        if count >= limit:
            return
        # Find first empty cell
        for i in range(SIZE):
            for j in range(SIZE):
                if b[i][j] == EMPTY:
                    for num in range(1, SIZE + 1):
                        if is_safe(b, i, j, num):
                            b[i][j] = num
                            backtrack()
                            b[i][j] = EMPTY
                            if count >= limit:
                                return
                    # After trying all numbers for this empty cell, backtrack
                    return
        # No empty found: one valid solution
        count += 1

    backtrack()
    return count


def remove_cells(board, clues):
    """Remove cells from a full `board` until `clues` remain, preserving
    uniqueness: a removal is kept only if the puzzle still has exactly one
    solution. If removing a cell creates multiple solutions, the value is
    restored and another cell is tried.

    This is slower than blind removal because each tentative removal runs a
    (limited) solver; we use `count_solutions(..., limit=2)` so counting stops
    as soon as a second solution is found.
    """
    attempts = SIZE * SIZE - clues
    # Get all positions and shuffle to randomize removals
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(positions)
    idx = 0
    while attempts > 0 and idx < len(positions):
        row, col = positions[idx]
        idx += 1
        if board[row][col] == EMPTY:
            continue
        # Tentatively remove
        removed = board[row][col]
        board[row][col] = EMPTY
        # If puzzle still has a unique solution, keep it removed
        sols = count_solutions(board, limit=2)
        if sols == 1:
            attempts -= 1
        else:
            # More than one solution or none --> restore and try others
            board[row][col] = removed

def generate_puzzle(clues=35):
    # Allow passing a difficulty name (e.g. 'easy') or an integer clue count.
    if isinstance(clues, str):
        clues = DIFFICULTY_LEVELS.get(clues.lower(), 35)
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
