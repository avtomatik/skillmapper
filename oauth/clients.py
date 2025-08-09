from http import HTTPStatus

import requests

from config.settings import Settings


class RequestsOAuthClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def exchange_code_for_token(self, auth_code: str) -> dict | None:
        data = self.settings.authorization_code_payload(auth_code)
        response = requests.post(self.settings.oauth.token_url, data=data)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        print("Token exchange failed:", response.status_code, response.text)
        return None

    def refresh_access_token(self, refresh_token: str) -> dict | None:
        data = self.settings.refresh_token_payload(refresh_token)
        response = requests.post(self.settings.oauth.token_url, data=data)
        if response.status_code == HTTPStatus.OK:
            print("Access token refreshed.")
            return response.json()
        print("Token refresh failed:", response.status_code, response.text)
        return None
