from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread
from urllib.parse import parse_qs, urlparse


class OAuthCallbackServer:
    def __init__(self, host: str, port: int, path: str, state: str):
        self._host = host
        self._port = port
        self._path = path
        self._state = state
        self._event = Event()
        self._code = None
        self._error = None
        self._server = None
        self._thread = None

    def start(self) -> None:
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path != owner._path:
                    self.send_error(404)
                    return
                query = parse_qs(parsed.query)
                if query.get("state", [None])[0] != owner._state:
                    owner._error = "OAuth callback state mismatch."
                    self.reply(400, "Authorization response rejected.")
                elif query.get("error", [None])[0]:
                    owner._error = "Authorization denied by HH.ru."
                    self.reply(400, "Authorization was not completed.")
                elif not query.get("code", [None])[0]:
                    owner._error = (
                        "Callback did not contain authorization code."
                    )
                    self.reply(400, "Authorization response was incomplete.")
                else:
                    owner._code = query["code"][0]
                    self.reply(
                        200, "Authorization complete. You may close this tab."
                    )
                owner._event.set()

            def reply(self, status, message):
                body = message.encode()
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                return

        self._server = ThreadingHTTPServer((self._host, self._port), Handler)
        self._server.daemon_threads = True
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def wait_for_code(self, timeout: float) -> str:
        if not self._event.wait(timeout):
            raise TimeoutError("Timed out waiting for HH.ru authorization.")
        if self._error:
            raise RuntimeError(self._error)
        if not self._code:
            raise RuntimeError("Authorization callback returned no code.")
        return self._code

    def close(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
