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
    # The landing page should contain language options
    assert b'language-option' in res.data
    # Khmer flag should be present
    assert '🇰🇭'.encode('utf-8') in res.data


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


def test_import_csv(client, tmp_path):
    import csv
    structure = app._load_questionnaire_structure()
    q_ids = [str(q["id"]) for q in structure.get("questions", [])]
    headers = ["timestamp", "id"] + [f"Q{qid}" for qid in q_ids] + ["G1", "G2", "G3", "G4", "G5", "G6"]
    row = ["2024-01-01T00:00:00Z", "import1"]
    row += ["a1"] + ["" for _ in q_ids[1:]]
    row += ["0"] * 6
    csv_path = tmp_path / "data.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(row)

    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    with open(csv_path, 'rb') as f:
        res = client.post('/admin/import_csv', data={'file': (f, 'data.csv')}, content_type='multipart/form-data')
        assert res.status_code == 302

    conn = sqlite3.connect(app.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM responses WHERE id=?", ("import1",))
    assert cur.fetchone() is not None
    conn.close()
