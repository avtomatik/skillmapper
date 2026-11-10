from requests import Session
from requests.exceptions import RequestException

from skillmapper.config.settings import OAuthSettings
from skillmapper.oauth.exceptions import (AuthorizationRequired, OAuthError,
                                          TokenRefreshError)


class RequestsOAuthClient:
    def __init__(self, settings: OAuthSettings, *, timeout: float = 15.0):
        self._settings = settings
        self._timeout = timeout
        self._session = Session()

    def close(self) -> None:
        self._session.close()

    def _post(self, payload: dict, *, refresh: bool) -> dict:
        try:
            response = self._session.post(
                self._settings.token_url, data=payload, timeout=self._timeout
            )
        except RequestException as exc:
            error = TokenRefreshError if refresh else OAuthError
            raise error("Could not reach HH.ru token endpoint.") from exc
        if refresh and response.status_code == 400:
            try:
                body = response.json()
            except ValueError:
                body = {}
            if isinstance(body, dict) and body.get("error"):
                raise AuthorizationRequired(
                    "Saved refresh token is invalid; authorize again."
                )
        if not response.ok:
            error = TokenRefreshError if refresh else OAuthError
            raise error(
                f"HH.ru token request failed (HTTP {response.status_code})."
            )
        try:
            data = response.json()
        except ValueError as exc:
            error = TokenRefreshError if refresh else OAuthError
            raise error("HH.ru returned invalid token JSON.") from exc
        if not isinstance(data, dict) or not data.get("access_token"):
            error = TokenRefreshError if refresh else OAuthError
            raise error("HH.ru token response has no access_token.")
        return data

    def exchange_code_for_token(self, auth_code: str) -> dict:
        return self._post(
            {
                "grant_type": "authorization_code",
                "code": auth_code,
                "client_id": self._settings.client_id,
                "client_secret": self._settings.client_secret.get_secret_value(),
                "redirect_uri": self._settings.redirect_uri,
            },
            refresh=False,
        )

    def refresh_access_token(self, refresh_token: str) -> dict:
        return self._post(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self._settings.client_id,
                "client_secret": self._settings.client_secret.get_secret_value(),
            },
            refresh=True,
        )
