import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'responses.db')

# Serve the survey front-end
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            products TEXT,
            features TEXT
        )"""
    )
    conn.commit()
    conn.close()

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True)
    response_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO responses (id, timestamp, products, features) VALUES (?, ?, ?, ?)',
                (response_id, timestamp, data.get('products'), data.get('features')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'id': response_id, 'timestamp': timestamp})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
