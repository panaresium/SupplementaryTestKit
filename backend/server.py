import json

import os
import uuid
import cgi
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from database import init_db, register_user, authenticate_user, save_questionnaire, get_questionnaires

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

init_db()
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class RequestHandler(BaseHTTPRequestHandler):
    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):

        if self.path == '/upload':
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type', ''))
            if ctype == 'multipart/form-data':
                pdict['boundary'] = pdict['boundary'].encode('utf-8')
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-Length', 0))
                fields = cgi.parse_multipart(self.rfile, pdict)
                files = fields.get('file')
                if files:
                    fname = str(uuid.uuid4())
                    path = os.path.join(UPLOAD_DIR, fname)
                    with open(path, 'wb') as f:
                        f.write(files[0])
                    self._set_json(201)
                    self.wfile.write(json.dumps({'path': f'/uploads/{fname}'}).encode('utf-8'))
                else:
                    self._set_json(400)
                    self.wfile.write(b'{"error":"file required"}')
            else:
                self._set_json(400)
                self.wfile.write(b'{"error":"bad content type"}')
            return

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

            return

        if parsed.path.startswith('/uploads/'):
            fname = os.path.basename(parsed.path)
            fpath = os.path.join(UPLOAD_DIR, fname)
            if os.path.isfile(fpath):
                self.send_response(200)
                ctype, _ = mimetypes.guess_type(fpath)
                self.send_header('Content-Type', ctype or 'application/octet-stream')
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        if parsed.path == '/' or parsed.path.startswith('/static'):
            if parsed.path == '/':
                fpath = os.path.join(STATIC_DIR, 'index.html')
            else:
                rel = parsed.path[len('/static/'):]
                fpath = os.path.join(STATIC_DIR, rel)
            if os.path.isfile(fpath):
                self.send_response(200)
                ctype, _ = mimetypes.guess_type(fpath)
                self.send_header('Content-Type', ctype or 'text/html')
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        self._set_json(404)
        self.wfile.write(b'{"error":"not found"}')


if __name__ == '__main__':
    addr = ('', 8000)
    HTTPServer(addr, RequestHandler).serve_forever()
