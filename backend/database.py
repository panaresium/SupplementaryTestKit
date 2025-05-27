import sqlite3
from hashlib import sha256
from typing import Optional, List

DB_PATH = 'supplementary.db'

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
"""

CREATE_QUEST = """
CREATE TABLE IF NOT EXISTS questionnaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    language_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(CREATE_USERS)
    c.execute(CREATE_QUEST)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return sha256(password.encode('utf-8')).hexdigest()


def register_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                     (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT password_hash FROM users WHERE username=?', (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    stored = row[0]
    return stored == hash_password(password)


def save_questionnaire(username: str, data: str, language_code: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT id FROM users WHERE username=?', (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    user_id = row[0]
    conn.execute('INSERT INTO questionnaires (user_id, data, language_code) VALUES (?, ?, ?)',
                 (user_id, data, language_code))
    conn.commit()
    conn.close()
    return True


def get_questionnaires(username: str) -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT id FROM users WHERE username=?', (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return []
    user_id = row[0]
    cur = conn.execute('SELECT data FROM questionnaires WHERE user_id=? ORDER BY created_at DESC',
                       (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
