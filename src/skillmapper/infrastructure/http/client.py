from collections.abc import Mapping
from typing import Any

import requests
from requests.auth import AuthBase


class HttpClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 15.0,
        auth: AuthBase | None = None,
    ):
        self._base_url = str(base_url).rstrip("/")
        self._timeout = timeout
        self._auth = auth
        self._session: requests.Session | None = None

    def __enter__(self):
        if self._session is not None:
            raise RuntimeError("HTTP client already connected.")
        self._session = requests.Session()
        self._session.auth = self._auth
        return self

    def __exit__(self, *_args):
        if self._session is not None:
            self._session.close()
            self._session = None

    def _request(self, method: str, path: str, **kwargs):
        if self._session is None:
            raise RuntimeError("HTTP client is not connected.")
        kwargs.setdefault("timeout", self._timeout)
        return self._session.request(
            method, f"{self._base_url}/{path.lstrip('/')}", **kwargs
        )

    def get(self, path: str, *, params: Mapping[str, Any] | None = None):
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        json: dict | None = None,
        data: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ):
        return self._request("POST", path, json=json, data=data, params=params)

    def patch(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: Mapping[str, Any] | None = None,
    ):
        return self._request("PATCH", path, json=json, params=params)
