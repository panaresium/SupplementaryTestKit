import json
import os
import mimetypes
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from database import init_db, register_user, authenticate_user, save_questionnaire, get_questionnaires

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

class RequestHandler(BaseHTTPRequestHandler):
    def _serve_file(self, path):
        if not os.path.exists(path):
            self.send_error(404)
            return
        ctype, _ = mimetypes.guess_type(path)
        if not ctype:
            ctype = 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

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
            ctype = self.headers.get('Content-Type', '')
            if not ctype.startswith('multipart/form-data'):
                self._set_json(400)
                self.wfile.write(b'{"error":"multipart required"}')
                return
            env = {'REQUEST_METHOD': 'POST'}
            fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            fileitem = fs['image'] if 'image' in fs else None
            if not fileitem or not fileitem.filename:
                self._set_json(400)
                self.wfile.write(b'{"error":"no image"}')
                return
            filename = os.path.basename(fileitem.filename)
            dest = os.path.join(UPLOAD_DIR, filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(UPLOAD_DIR, f"{base}_{counter}{ext}")
                counter += 1
            with open(dest, 'wb') as f:
                f.write(fileitem.file.read())
            self._set_json(201)
            self.wfile.write(json.dumps({'file': os.path.basename(dest)}).encode())
        else:
            self._set_json(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            self._serve_file(os.path.join(STATIC_DIR, 'index.html'))
        elif parsed.path.startswith('/static/'):
            rel = parsed.path[len('/static/') :]
            self._serve_file(os.path.join(STATIC_DIR, rel))
        elif parsed.path.startswith('/uploads/'):
            rel = parsed.path[len('/uploads/') :]
            self._serve_file(os.path.join(UPLOAD_DIR, rel))
        elif parsed.path.startswith('/questionnaire/'):
            username = parsed.path.split('/')[-1]
            data = get_questionnaires(username)
            self._set_json(200)
            self.wfile.write(json.dumps({'data': data}).encode('utf-8'))
        else:
            self._set_json(404)
            self.wfile.write(b'{"error":"not found"}')

if __name__ == '__main__':
    addr = ('', 8000)
    HTTPServer(addr, RequestHandler).serve_forever()
