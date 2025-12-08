from http import HTTPStatus
from typing import Optional

import requests

from config.conf import conf


class RequestsOAuthClient:
    def exchange_code_for_token(self, auth_code: str) -> Optional[dict]:
        data = conf.authorization_code_payload(auth_code)
        resp = requests.post(conf.TOKEN_URL, data=data)
        if resp.status_code == HTTPStatus.OK:
            return resp.json()
        print("Token exchange failed:", resp.status_code, resp.text)
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        data = conf.refresh_token_payload(refresh_token)
        resp = requests.post(conf.TOKEN_URL, data=data)
        if resp.status_code == HTTPStatus.OK:
            print("Access token refreshed.")
            return resp.json()
        print("Token refresh failed:", resp.status_code, resp.text)
        return None
