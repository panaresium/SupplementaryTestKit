import json
import os
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from cgi import FieldStorage

from database import (
    init_db,
    register_user,
    authenticate_user,
    save_questionnaire,
    get_questionnaires,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')
UPLOAD_DIR = os.path.join(BASE_DIR, '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

class RequestHandler(BaseHTTPRequestHandler):
    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _serve_file(self, path, content_type='application/octet-stream'):
        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body or b'{}')
        except json.JSONDecodeError:
            self._set_json(400)
            self.wfile.write(b'{"error": "Invalid JSON"}')
            return

        if self.path == '/register':
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                self._set_json(400)
                self.wfile.write(b'{"error":"username and password required"}')
                return
            success = register_user(username, password)
            if success:
                self._set_json(201)
                self.wfile.write(b'{"status":"registered"}')
            else:
                self._set_json(409)
                self.wfile.write(b'{"error":"user exists"}')
        elif self.path == '/login':
            username = data.get('username')
            password = data.get('password')
            if authenticate_user(username, password):
                self._set_json(200)
                self.wfile.write(b'{"status":"ok"}')
            else:
                self._set_json(401)
                self.wfile.write(b'{"error":"invalid credentials"}')
        elif self.path == '/questionnaire':
            username = data.get('username')
            answers = data.get('answers')
            if not isinstance(answers, dict):
                self._set_json(400)
                self.wfile.write(b'{"error":"answers must be object"}')
                return
            saved = save_questionnaire(username, json.dumps(answers))
            if saved:
                self._set_json(201)
                self.wfile.write(b'{"status":"saved"}')
            else:
                self._set_json(400)
                self.wfile.write(b'{"error":"unknown user"}')
        elif self.path == '/upload':
            form = FieldStorage(fp=self.rfile, headers=self.headers,
                               environ={'REQUEST_METHOD': 'POST'})
            user = form.getvalue('username')
            fileitem = form['image'] if 'image' in form else None
            if not user or not fileitem:
                self._set_json(400)
                self.wfile.write(b'{"error":"username and image required"}')
                return
            ext = os.path.splitext(fileitem.filename)[1]
            fname = uuid.uuid4().hex + ext
            fpath = os.path.join(UPLOAD_DIR, fname)
            with open(fpath, 'wb') as f:
                f.write(fileitem.file.read())
            self._set_json(201)
            self.wfile.write(json.dumps({'path': f'/uploads/{fname}'}).encode())
        else:
            self._set_json(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/questionnaire/'):
            username = parsed.path.split('/')[-1]
            data = get_questionnaires(username)
            self._set_json(200)
            self.wfile.write(json.dumps({'data': data}).encode('utf-8'))
        elif parsed.path.startswith('/uploads/'):
            fpath = os.path.join(UPLOAD_DIR, os.path.basename(parsed.path))
            self._serve_file(fpath, 'application/octet-stream')
        elif parsed.path == '/' or parsed.path.startswith('/static/'):
            if parsed.path == '/':
                rel = 'index.html'
            else:
                rel = parsed.path[len('/static/'):]  # may be ''
            fpath = os.path.join(STATIC_DIR, rel)
            ctype = 'text/html' if fpath.endswith('.html') else 'application/octet-stream'
            self._serve_file(fpath, ctype)
        else:
            self._set_json(404)
            self.wfile.write(b'{"error":"not found"}')

if __name__ == '__main__':
    addr = ('', 8000)
    HTTPServer(addr, RequestHandler).serve_forever()
