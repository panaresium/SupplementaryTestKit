import os
import sqlite3
import json # Added json import
from flask import Flask, request, jsonify, send_from_directory, render_template # Added render_template
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime, timezone # Updated import

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'responses.db')

# Serve the survey front-end
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/thank_you.html')
def thank_you():
    return send_from_directory('static', 'thank_you.html')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS responses")
    conn.commit() 
    
    create_table_sql = """CREATE TABLE IF NOT EXISTS responses (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        language_code TEXT,
        answers_json TEXT,
        products TEXT
    )"""
    cur.execute(create_table_sql)
    conn.commit()
    conn.close()

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True)
    language_code = data.get('language')
    answers_dict = data.get('answers')
    products_data = "" # Default to empty string

    if not answers_dict: # Basic validation
        return jsonify({'error': 'Missing answers data'}), 400
    if not language_code: # Basic validation for language_code
        return jsonify({'error': 'Missing language code'}), 400

    answers_json_str = json.dumps(answers_dict)
    
    response_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    column_names = ["id", "timestamp", "language_code", "answers_json", "products"]
    
    placeholders = ", ".join(["?"] * len(column_names))
    sql = f"INSERT INTO responses ({', '.join(column_names)}) VALUES ({placeholders})"
    
    values_tuple = (
        response_id, 
        timestamp, 
        language_code, 
        answers_json_str,
        products_data 
    )

    cur.execute(sql, values_tuple)
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'id': response_id, 'timestamp': timestamp})

@app.route('/admin/results')
def admin_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()
    cur.execute("SELECT * FROM responses ORDER BY timestamp DESC")
    results = cur.fetchall()
    conn.close()
    
    processed_results = []
    for row in results:
        row_dict = dict(row) 
        if row_dict.get('answers_json'):
            try:
                row_dict['answers_json'] = json.loads(row_dict['answers_json'])
            except json.JSONDecodeError:
                # Keep as original string if parsing fails, or set to an error indicator
                row_dict['answers_json'] = {"error": "Failed to parse answers JSON"}
        processed_results.append(row_dict)
    
    return render_template('results.html', results=processed_results)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
