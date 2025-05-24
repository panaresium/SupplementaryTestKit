import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from database import init_db, register_user, authenticate_user, save_questionnaire, get_questionnaires

init_db()

class RequestHandler(BaseHTTPRequestHandler):
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
        else:
            self._set_json(404)
            self.wfile.write(b'{"error":"not found"}')

if __name__ == '__main__':
    addr = ('', 8000)
    HTTPServer(addr, RequestHandler).serve_forever()
