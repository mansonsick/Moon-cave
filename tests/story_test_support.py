"""Local Pages-prefix server shared by Story 02 browser checks."""
import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if route.startswith('/Moon-cave/'):
            target = (REPO/route[len('/Moon-cave/'):]).resolve()
            if target.is_relative_to(REPO): return str(target)
        return str(REPO/'__no_such_route__')
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204); self.end_headers(); return
        super().do_GET()

def serve():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    return server, f'http://127.0.0.1:{server.server_port}/Moon-cave/'
