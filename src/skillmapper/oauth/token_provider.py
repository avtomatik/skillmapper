import time
from threading import RLock
from typing import Callable

from skillmapper.oauth.exceptions import AuthorizationRequired, OAuthError
from skillmapper.oauth.protocols import OAuthClient, TokenStore


class OAuthTokenProvider:
    def __init__(
        self,
        client: OAuthClient,
        store: TokenStore,
        *,
        clock: Callable[[], float] = time.time,
        expiry_skew: float = 60.0,
    ):
        self._client = client
        self._store = store
        self._clock = clock
        self._skew = expiry_skew
        self._lock = RLock()
        self._tokens = store.load_tokens()

    @property
    def has_refresh_token(self) -> bool:
        return bool(self._tokens and self._tokens.get("refresh_token"))

    def install_tokens(self, tokens: dict) -> None:
        with self._lock:
            merged = self._merge(tokens)
            self._validate(merged)
            merged["expires_at"] = self._expiry(tokens)
            self._store.save_tokens(merged)
            self._tokens = merged

    def get_access_token(self) -> str:
        with self._lock:
            if not self._tokens:
                raise AuthorizationRequired(
                    "No saved tokens; authorize with HH.ru."
                )
            token = self._tokens.get("access_token")
            expiry = float(self._tokens.get("expires_at", 0))
            if token and self._clock() < expiry - self._skew:
                return str(token)
            refresh = self._tokens.get("refresh_token")
            if not refresh:
                raise AuthorizationRequired(
                    "Expired access token and no refresh token."
                )
            refreshed = self._client.refresh_access_token(str(refresh))
            merged = self._merge(refreshed)
            self._validate(merged)
            merged["expires_at"] = self._expiry(refreshed)
            self._store.save_tokens(merged)
            self._tokens = merged
            return str(merged["access_token"])

    def _merge(self, incoming: dict) -> dict:
        merged = dict(self._tokens or {})
        old_refresh = merged.get("refresh_token")
        merged.update(incoming)
        if not incoming.get("refresh_token") and old_refresh:
            merged["refresh_token"] = old_refresh
        return merged

    def _expiry(self, tokens: dict) -> float:
        try:
            seconds = float(tokens.get("expires_in", 3600))
        except (TypeError, ValueError) as exc:
            raise OAuthError("Invalid expires_in in token response.") from exc
        if seconds <= 0:
            raise OAuthError("expires_in must be positive.")
        return self._clock() + seconds

    @staticmethod
    def _validate(tokens: dict) -> None:
        if not tokens.get("access_token"):
            raise OAuthError("Token response did not contain access_token.")
