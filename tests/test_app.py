import json
import os
import sys
import sqlite3
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "responses.db"
    monkeypatch.setattr(app, "DB_PATH", str(db_path))
    app.init_db()
    app.app.config.update(TESTING=True)
    with app.app.test_client() as client:
        yield client


def test_index_route(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'<!DOCTYPE html>' in res.data


def test_submit_and_admin_results(client):
    payload = {"language": "en", "answers": {"1": "a1"}}
    res = client.post('/api/submit', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "success"
    assert "id" in data
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    res_admin = client.get('/admin/results')
    assert res_admin.status_code == 200
    assert b'Survey Submissions' in res_admin.data
