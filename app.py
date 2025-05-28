import os
import sqlite3
import csv
import io
import json  # Added json import
from collections import defaultdict, Counter
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template,
    session,
    redirect,
    url_for,
    Response,
)
import openai

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv may not be installed during testing
    def load_dotenv():
        return False

from flask_cors import CORS
from uuid import uuid4
from datetime import datetime, timezone # Updated import

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
CORS(app)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# Mapping of group IDs to descriptive names
GROUP_NAMES = {
    "G1": "Office/Digital",
    "G2": "Medical/Caregiving",
    "G3": "Industrial/Factory",
    "G4": "Heavy Labor/Construction",
    "G5": "Service Sector",
    "G6": "Agriculture/Fishery",
}

# Mapping of language codes to human-readable names
LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "th": "Thai",
}

DB_PATH = os.path.join(os.path.dirname(__file__), 'responses.db')


ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}

from functools import wraps

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# Serve the survey front-end
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/auth/google')
def google_auth():
    """Placeholder route for Google OAuth integration."""
    # In a full implementation, this would start the OAuth flow and upon
    # success mark the admin as authenticated via Google.
    session['logged_in'] = True
    session['username'] = ADMIN_CREDENTIALS['username']
    return redirect(url_for('admin_dashboard'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

from urllib.parse import unquote


def _load_questionnaire_structure() -> dict:
    path = os.path.join(app.root_path, 'static', 'questionnaire_structure.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


GROUP_INFO_FILE = os.path.join(os.path.dirname(__file__), 'group_info.json')
KEYWORD_FILE = os.path.join(os.path.dirname(__file__), 'thai_keywords.json')


def _load_group_info() -> dict:
    if os.path.exists(GROUP_INFO_FILE):

        with open(GROUP_INFO_FILE, 'r', encoding='utf-8') as f:

            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    # Default structure if file does not exist or is invalid
    return {
        "G1": {"message": "", "image": ""},
        "G2": {"message": "", "image": ""},
        "G3": {"message": "", "image": ""},
        "G4": {"message": "", "image": ""},
        "G5": {"message": "", "image": ""},
        "G6": {"message": "", "image": ""},
    }


def _save_group_info(data: dict):

    with open(GROUP_INFO_FILE, 'w', encoding='utf-8') as f:

        json.dump(data, f, indent=2)


def _load_keywords() -> dict:
    """Load keyword categories from KEYWORD_FILE."""
    if os.path.exists(KEYWORD_FILE):
        with open(KEYWORD_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {}


def _calculate_scores(user_answers: dict, structure: dict, lang_code: str = "en"):
    group_scores = {"G1": 0, "G2": 0, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    submitted = []

    for q in structure.get('questions', []):
        qid = str(q.get('id'))
        if qid not in user_answers:
            continue
        val = user_answers[qid]
        text = q.get('questionText', {}).get(lang_code, q.get('questionText', {}).get('en', ''))
        display = 'N/A'

        if q.get('type') == 'radio':
            if val not in (None, ''):
                opt = next((o for o in q.get('answers', []) if o.get('value') == val), None)
                if opt:
                    display = opt.get('text', {}).get(lang_code, opt.get('text', {}).get('en', val))
                    for g, w in opt.get('weights', {}).items():
                        if g in group_scores and isinstance(w, (int, float)):
                            group_scores[g] += w
                else:
                    display = f"Selected value not found: {val}"
        elif q.get('type') == 'checkbox_group':
            if isinstance(val, list) and val:
                texts = []
                for choice in val:
                    opt = next((o for o in q.get('answers', []) if o.get('value') == choice), None)
                    if opt:
                        texts.append(opt.get('text', {}).get(lang_code, opt.get('text', {}).get('en', choice)))
                        for g, w in opt.get('weights', {}).items():
                            if g in group_scores and isinstance(w, (int, float)):
                                group_scores[g] += w
                    else:
                        texts.append(f"Value not found: {choice}")
                display = ", ".join(texts)
        elif q.get('type') == 'freetext':
            if val not in (None, ''):
                display = str(val)
        else:
            if isinstance(val, dict):
                display = "; ".join(f"{k}: {v}" for k, v in val.items())
            elif isinstance(val, list):
                display = ", ".join(map(str, val))
            elif val not in (None, ''):
                display = str(val)

        submitted.append((text, display))

    return group_scores, submitted


def _generate_recommendation(group_scores: dict) -> str:

    scores = sorted(group_scores.items(), key=lambda kv: kv[1], reverse=True)
    recs = []
    if scores:
        recs.append(scores[0])
        if len(scores) > 1 and (scores[0][1] - scores[1][1] <= 5):
            recs.append(scores[1])

    if not recs:
        return "No specific profile alignment found based on current scores."

    if len(recs) == 1:
        key, _ = recs[0]
        return f"Your profile suggests you align with: {GROUP_NAMES.get(key, key)} ({key})."

    group_texts = [f"{GROUP_NAMES.get(k, k)} ({k})" for k, _ in recs]
    return f"Your profile suggests you align with: {' and '.join(group_texts)}."


def _ai_suggestion(text: str, lang_code: str, groups=None) -> str:

    """Query OpenAI for a supplement suggestion based on user text."""
    if not text or not text.strip():
        return ""
    try:

        language_name = LANGUAGE_NAMES.get(lang_code, LANGUAGE_NAMES.get("th", "Thai"))
        group_info = ""
        if groups:
            names = [GROUP_NAMES.get(g, g) for g in groups]
            group_info = f" The user aligns with: {', '.join(names)}."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant providing supplement advice. "
                    "You will suggest supplements based on the six groups "
                    "G1=Office/Digital,G2=Medical/Caregiving,G3=Industrial/Factory,"
                    "G4=Heavy Labor/Construction,G5=Service Sector,G6=Agriculture/Fishery."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Please respond in {language_name} based on the following concerns: {text}. "
                    f"{group_info} Suggest ways to exercise, relax, and take supplements for better health."

                ),
            },
        ]
        resp = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)
        return resp.choices[0].message["content"].strip()
    except Exception as exc:
        return f"AI suggestion unavailable: {exc}"


@app.route('/thank_you.html')
def thank_you():
    data_param = request.args.get('data')
    if not data_param:
        return render_template('thank_you.html', submitted_answers=None, group_scores=None,
                               recommendation_text=None)

    try:
        decoded = unquote(data_param)
        answers = json.loads(decoded)
    except Exception as exc:
        return f"Invalid data parameter: {exc}", 400

    language = request.args.get('lang', 'th')
    structure = _load_questionnaire_structure()
    scores, submitted = _calculate_scores(answers, structure, language)
    recommendation = _generate_recommendation(scores)


    # Determine the user's top groups for tailored AI advice

    top_groups = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    rec_groups = []
    if top_groups:
        rec_groups.append(top_groups[0][0])
        if len(top_groups) > 1 and (top_groups[0][1] - top_groups[1][1] <= 5):
            rec_groups.append(top_groups[1][0])

    # Use the freetext from the last question for AI suggestion
    last_text = answers.get('10', '')

    ai_suggestion = _ai_suggestion(last_text, language, rec_groups)

    group_info = _load_group_info()


    return render_template(
        'thank_you.html',
        submitted_answers=submitted,
        group_scores=scores,
        recommendation_text=recommendation,
        ai_suggestion=ai_suggestion,
        group_info=group_info,
        rec_groups=rec_groups,
        language_code=language,
    )

def init_db():
    """Create the responses table if it does not already exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS responses (
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
@admin_required
def admin_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()
    cur.execute("SELECT * FROM responses ORDER BY timestamp DESC")
    results = cur.fetchall()
    conn.close()
    
    structure = _load_questionnaire_structure()

    q_map = {str(q["id"]): q.get("questionText", {}).get("en", f"Q{q['id']}")
             for q in structure.get("questions", [])}
    aggregate_scores = {"G1": 0, "G2": 0, "G3": 0, "G4": 0, "G5": 0, "G6": 0}
    question_counts = {}
    for q in structure.get("questions", []):
        if q.get("type") == "freetext":
            continue
        qid = str(q["id"])
        question_counts[qid] = {ans.get("value"): 0 for ans in q.get("answers", [])}

    free_texts = []
    # store raw history for correlation
    score_history_raw = {"timestamps": [], "G1": [], "G2": [], "G3": [], "G4": [], "G5": [], "G6": []}
    # daily aggregation helpers
    daily_totals = defaultdict(lambda: {g: 0 for g in aggregate_scores})
    daily_counts = defaultdict(int)
    keywords_map = _load_keywords()

    processed_results = []
    for row in results:
        row_dict = dict(row)
        answers = {}
        if row_dict.get('answers_json'):
            try:
                answers = json.loads(row_dict['answers_json'])
            except json.JSONDecodeError:
                answers = {}
        for qid in q_map.keys():
            row_dict[f"Q{qid}"] = answers.get(str(qid), '')
        row_dict.pop('answers_json', None)
        row_dict.pop('products', None)
        scores, _ = _calculate_scores(answers, structure)
        row_dict.update(scores)
        for g in aggregate_scores:
            aggregate_scores[g] += scores[g]
            score_history_raw[g].append(scores[g])
        score_history_raw["timestamps"].append(row_dict["timestamp"])
        day = row_dict["timestamp"][:10]
        daily_counts[day] += 1
        for g in aggregate_scores:
            daily_totals[day][g] += scores[g]
        for q in structure.get("questions", []):
            qid = str(q.get("id"))
            val = answers.get(qid)
            if q.get("type") == "freetext":
                if val:
                    free_texts.append(val)
            elif q.get("type") == "checkbox_group":
                if isinstance(val, list):
                    for choice in val:
                        question_counts[qid][choice] = question_counts[qid].get(choice, 0) + 1
            else:
                if val is not None:
                    question_counts[qid][val] = question_counts[qid].get(val, 0) + 1
        processed_results.append(row_dict)

    # build daily score history averaging scores per day
    sorted_days = sorted(daily_totals.keys())
    score_history = {"dates": sorted_days}
    for g in aggregate_scores:
        score_history[g] = [daily_totals[d][g] / daily_counts[d] for d in sorted_days]

    # keyword summary for free text responses using predefined Thai terms
    keyword_counts = Counter()
    for text in free_texts:
        for words in keywords_map.values():
            for word in words:
                cnt = text.count(word)
                if cnt:
                    keyword_counts[word] += cnt

    headers = [f"Q{qid}" for qid in q_map.keys()] + list(aggregate_scores.keys())
    averages = {g: (aggregate_scores[g]/len(results) if results else 0) for g in aggregate_scores}

    def _corr(xs, ys):
        n = len(xs)
        if n == 0:
            return 0
        mean_x = sum(xs)/n
        mean_y = sum(ys)/n
        num = sum((x-mean_x)*(y-mean_y) for x, y in zip(xs, ys))
        den_x = sum((x-mean_x)**2 for x in xs)
        den_y = sum((y-mean_y)**2 for y in ys)
        denom = (den_x * den_y) ** 0.5
        return num/denom if denom else 0

    groups = list(aggregate_scores.keys())
    correlations = {g1: {g2: _corr(score_history_raw[g1], score_history_raw[g2]) for g2 in groups} for g1 in groups}
    return render_template(
        'results.html',
        results=processed_results,
        totals=aggregate_scores,
        averages=averages,
        headers=headers,
        q_map=q_map,
        question_counts=question_counts,
        free_texts=free_texts,
        keyword_counts=dict(keyword_counts),
        score_history=score_history,
        correlations=correlations
    )


@app.route('/admin/export_csv')
@admin_required
def admin_export_csv():
    """Export all survey results as a CSV file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM responses ORDER BY timestamp DESC")
    results = cur.fetchall()
    conn.close()

    structure = _load_questionnaire_structure()
    q_map = {str(q["id"]): q.get("questionText", {}).get("en", f"Q{q['id']}")
             for q in structure.get("questions", [])}
    headers = ["timestamp", "id"] + [f"Q{qid}" for qid in q_map.keys()]
    headers += ["G1", "G2", "G3", "G4", "G5", "G6"]

    from io import StringIO
    output_io = StringIO()
    writer = csv.writer(output_io)

    writer.writerow(headers)
    for row in results:
        row_dict = dict(row)
        answers = {}
        if row_dict.get("answers_json"):
            try:
                answers = json.loads(row_dict["answers_json"])
            except json.JSONDecodeError:
                answers = {}
        scores, _ = _calculate_scores(answers, structure)
        values = [row_dict["timestamp"], row_dict["id"]]
        for qid in q_map.keys():
            values.append(answers.get(str(qid), ""))
        values.extend([scores[g] for g in ["G1", "G2", "G3", "G4", "G5", "G6"]])
        writer.writerow(values)

    csv_data = output_io.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"}
    )


@app.route('/admin/import_csv', methods=['POST'])
@admin_required
def admin_import_csv():
    """Import survey results from a CSV file."""
    file = request.files.get('file')
    if not file or file.filename == '':
        return redirect(url_for('admin_results'))

    try:
        stream = io.StringIO(file.read().decode('utf-8'))
    except Exception:
        return redirect(url_for('admin_results'))

    reader = csv.DictReader(stream)
    structure = _load_questionnaire_structure()
    question_ids = [str(q.get('id')) for q in structure.get('questions', [])]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for row in reader:
        response_id = row.get('id') or str(uuid4())
        timestamp = row.get('timestamp') or datetime.now(timezone.utc).isoformat()
        answers = {qid: row.get(f'Q{qid}', '') for qid in question_ids if row.get(f'Q{qid}', '')}
        answers_json = json.dumps(answers)
        cur.execute('SELECT 1 FROM responses WHERE id=?', (response_id,))
        if cur.fetchone():
            continue
        cur.execute(
            'INSERT INTO responses (id, timestamp, language_code, answers_json, products) '
            'VALUES (?, ?, ?, ?, ?)',
            (response_id, timestamp, '', answers_json, '')
        )
    conn.commit()
    conn.close()

    return redirect(url_for('admin_results'))

@app.route('/admin/group_info', methods=['GET', 'POST'])
@admin_required
def admin_group_info():
    group_info = _load_group_info()
    if request.method == 'POST':
        for gid in group_info.keys():
            group_info[gid]['message'] = request.form.get(f'{gid}_message', '')
            group_info[gid]['image'] = request.form.get(f'{gid}_image', '')
        _save_group_info(group_info)
    return render_template('group_info.html', group_info=group_info)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
