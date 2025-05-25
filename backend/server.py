import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from email.parser import BytesParser
from email.policy import default

from database import (
    init_db,
    register_user,
    authenticate_user,
    save_questionnaire,
    get_questionnaires,
)

STATIC_DIR = 'static'
UPLOAD_DIR = 'uploads'
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()


def parse_multipart(content_type: str, body: bytes):
    header = f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8')
    msg = BytesParser(policy=default).parsebytes(header + body)
    fields = {}
    files = {}
    for part in msg.iter_parts():
        name = part.get_param('name', header='content-disposition')
        filename = part.get_filename()
        data = part.get_payload(decode=True)
        if filename:
            files[name] = {'filename': filename, 'content': data}
        else:
            fields[name] = data.decode('utf-8')
    return fields, files


class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        if self.path == '/upload':
            ctype = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in ctype:
                self._send_json({'error': 'multipart required'}, 400)
                return
            fields, files = parse_multipart(ctype, body)
            img = files.get('image')
            if not img:
                self._send_json({'error': 'no image'}, 400)
                return
            fname = os.path.basename(img['filename'])
            path = os.path.join(UPLOAD_DIR, fname)
            with open(path, 'wb') as f:
                f.write(img['content'])
            self._send_json({'url': f'/uploads/{fname}'}, 201)
            return

        try:
            data = json.loads(body or b'{}')
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
            return

        if self.path == '/register':
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                self._send_json({'error': 'username and password required'}, 400)
                return
            if register_user(username, password):
                self._send_json({'status': 'registered'}, 201)
            else:
                self._send_json({'error': 'user exists'}, 409)
        elif self.path == '/login':
            username = data.get('username')
            password = data.get('password')
            if authenticate_user(username, password):
                self._send_json({'status': 'ok'})
            else:
                self._send_json({'error': 'invalid credentials'}, 401)
        elif self.path == '/questionnaire':
            username = data.get('username')
            answers = data.get('answers')
            if not isinstance(answers, dict):
                self._send_json({'error': 'answers must be object'}, 400)
                return
            if save_questionnaire(username, json.dumps(answers)):
                self._send_json({'status': 'saved'}, 201)
            else:
                self._send_json({'error': 'unknown user'}, 400)
        else:
            self._send_json({'error': 'not found'}, 404)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            self.serve_static('index.html')
        elif parsed.path.startswith('/static/'):
            self.serve_static(parsed.path[len('/static/'):])
        elif parsed.path.startswith('/uploads/'):
            self.serve_upload(parsed.path[len('/uploads/'):])
        elif parsed.path.startswith('/questionnaire/'):
            username = parsed.path.split('/')[-1]
            data = get_questionnaires(username)
            self._send_json({'data': data})
        else:
            self._send_json({'error': 'not found'}, 404)

    def serve_static(self, filename):
        path = os.path.join(STATIC_DIR, filename)
        if not os.path.isfile(path):
            self._send_json({'error': 'not found'}, 404)
            return
        self.send_response(200)
        if filename.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif filename.endswith('.css'):
            self.send_header('Content-Type', 'text/css')
        else:
            self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def serve_upload(self, filename):
        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            self._send_json({'error': 'not found'}, 404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())


if __name__ == '__main__':
    HTTPServer(('', 8000), RequestHandler).serve_forever()
