import hashlib
import json
from pathlib import Path
from flask import Flask, request, redirect, send_from_directory, abort

app = Flask(__name__)

DATA_PATH = Path('data/submissions.json')
DATA_PATH.parent.mkdir(exist_ok=True)
DATA_PATH.touch(exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/privacy_policy.html')
def privacy_policy():
    return send_from_directory('static', 'privacy_policy.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Ensure consent was provided
    if not request.form.get('consent'):
        abort(400, 'Consent is required')

    # Only store fields that are necessary
    name = request.form.get('name')
    email = request.form.get('email')
    comment = request.form.get('comment')

    # Pseudonymize email by hashing
    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()

    record = {
        'name': name,
        'email_hash': email_hash,
        'comment': comment
    }

    with open(DATA_PATH, 'a') as f:
        json.dump(record, f)
        f.write('\n')

    return 'Submission received. Thank you!'

if __name__ == '__main__':
    # Use SSL context for HTTPS in development. In production, run behind a
    # reverse proxy that terminates TLS.
    app.run(ssl_context='adhoc')
