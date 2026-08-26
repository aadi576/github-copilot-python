import os
import sys

# Ensure the parent folder (starter) is on sys.path so tests work when
# running pytest from repository root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import CURRENT, app as flask_app
import sudoku_logic


def test_index_returns_200():
    client = flask_app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200


def test_check_rejects_malformed_board():
    client = flask_app.test_client()
    resp = client.post('/check', json={'board': [[0]]})

    assert resp.status_code == 400
    assert resp.get_json()['error']


def test_check_rejects_well_formed_board_without_game(monkeypatch):
    monkeypatch.setitem(CURRENT, 'puzzle', None)
    monkeypatch.setitem(CURRENT, 'solution', None)
    board = [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]
    client = flask_app.test_client()

    resp = client.post('/check', json={'board': board})

    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'No game in progress'


def test_check_accepts_well_formed_board_after_new_game():
    client = flask_app.test_client()
    new_game_resp = client.get('/new')
    board = [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]

    resp = client.post('/check', json={'board': board})

    assert new_game_resp.status_code == 200
    assert resp.status_code == 200
    assert 'incorrect' in resp.get_json()
    assert 'complete' in resp.get_json()
