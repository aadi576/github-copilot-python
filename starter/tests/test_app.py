import os
import sys

# Ensure the parent folder (starter) is on sys.path so tests work when
# running pytest from repository root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


def test_index_returns_200():
    client = flask_app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
