import time
from typing import Optional


class InMemoryTokenStore:
    def __init__(self) -> None:
        self._data = {
            'access_token': None,
            'refresh_token': None,
            'expires_at': 0.0
        }

    def get_access_token(self) -> Optional[str]:
        return self._data['access_token']

    def get_refresh_token(self) -> Optional[str]:
        return self._data['refresh_token']

    def get_expiry(self) -> float:
        return self._data['expires_at']

    def save_tokens(self, tokens: dict) -> None:
        self._data['access_token'] = tokens['access_token']
        self._data['refresh_token'] = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)
        self._data['expires_at'] = time.time() + expires_in
