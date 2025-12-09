import threading
import time
from http import HTTPStatus

from flask import Flask, request

from config.conf import conf
from oauth.protocols import BrowserLauncher, OAuthClient, TokenStore


class OAuthService:
    def __init__(
        self,
        client: OAuthClient,
        token_store: TokenStore,
        browser: BrowserLauncher,
        port: int,
    ) -> None:
        self.client = client
        self.token_store = token_store
        self.browser = browser
        self.port = port
        self._app = Flask(__name__)
        self._auth_code: str | None = None
        self._register_routes()

    def _register_routes(self) -> None:
        @self._app.route("/callback")
        def callback():
            code = request.args.get("code")
            if not code:
                return "Authorization code not found.", HTTPStatus.BAD_REQUEST
            self._auth_code = code
            return "Authorization complete. You can close this tab."

    def start_oauth_flow(self) -> dict | None:
        threading.Thread(
            target=lambda: self._app.run(port=self.port), daemon=True
        ).start()

        self.browser.open(conf.auth_url)
        print("Waiting for user authorization...")

        while self._auth_code is None:
            time.sleep(0.5)

        tokens = self.client.exchange_code_for_token(self._auth_code)
        if tokens:
            self.token_store.save_tokens(tokens)
        return tokens

    def get_valid_access_token(self) -> str:
        if time.time() >= self.token_store.get_expiry():
            print("Access token expired — refreshing...")
            refreshed = self.client.refresh_access_token(
                self.token_store.get_refresh_token()
            )
            if refreshed:
                self.token_store.save_tokens(refreshed)
        return self.token_store.get_access_token()
