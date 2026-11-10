import secrets

from skillmapper.config.settings import OAuthSettings
from skillmapper.oauth.callback import OAuthCallbackServer
from skillmapper.oauth.protocols import BrowserLauncher, OAuthClient
from skillmapper.oauth.token_provider import OAuthTokenProvider


class OAuthFlow:
    def __init__(
        self,
        settings: OAuthSettings,
        client: OAuthClient,
        browser: BrowserLauncher,
        provider: OAuthTokenProvider,
    ):
        self._settings = settings
        self._client = client
        self._browser = browser
        self._provider = provider

    def authorize(self) -> None:
        state = secrets.token_urlsafe(32)
        callback = OAuthCallbackServer(
            self._settings.redirect_host,
            self._settings.redirect_port,
            self._settings.redirect_path,
            state,
        )
        try:
            callback.start()
            self._browser.open(self._settings.authorization_url(state))
            print("Waiting for HH.ru authorization in your browser...")
            code = callback.wait_for_code(self._settings.authorization_timeout)
            self._provider.install_tokens(
                self._client.exchange_code_for_token(code)
            )
        finally:
            callback.close()
