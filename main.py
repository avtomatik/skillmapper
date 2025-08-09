import threading
import time
import webbrowser
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Optional, Protocol

import requests
from flask import Flask, request

from config import conf


# === Protocols ===
class TokenStore(Protocol):
    def get_access_token(self) -> Optional[str]: ...
    def get_refresh_token(self) -> Optional[str]: ...
    def get_expiry(self) -> float: ...
    def save_tokens(self, tokens: dict) -> None: ...


class OAuthClient(Protocol):
    def exchange_code_for_token(self, auth_code: str) -> Optional[dict]: ...
    def refresh_access_token(self, refresh_token: str) -> Optional[dict]: ...


class BrowserLauncher(Protocol):
    def open(self, url: str) -> None: ...


# === Implementations ===
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


class RequestsOAuthClient:
    def exchange_code_for_token(self, auth_code: str) -> Optional[dict]:
        data = conf.authorization_code_payload(auth_code)
        resp = requests.post(conf.TOKEN_URL, data=data)
        if resp.status_code == HTTPStatus.OK:
            return resp.json()
        print('Token exchange failed:', resp.status_code, resp.text)
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        data = conf.refresh_token_payload(refresh_token)
        resp = requests.post(conf.TOKEN_URL, data=data)
        if resp.status_code == HTTPStatus.OK:
            print('Access token refreshed.')
            return resp.json()
        print('Token refresh failed:', resp.status_code, resp.text)
        return None


class WebBrowserLauncher:
    def open(self, url: str) -> None:
        webbrowser.open(url)


# === OAuth Service ===
class OAuthService:
    def __init__(
        self,
        client: OAuthClient,
        token_store: TokenStore,
        browser: BrowserLauncher,
        port: int
    ) -> None:
        self.client = client
        self.token_store = token_store
        self.browser = browser
        self.port = port
        self._app = Flask(__name__)
        self._auth_code: Optional[str] = None
        self._register_routes()

    def _register_routes(self) -> None:
        @self._app.route('/callback')
        def callback():
            code = request.args.get('code')
            if not code:
                return 'Authorization code not found.', HTTPStatus.BAD_REQUEST
            self._auth_code = code
            return 'Authorization complete. You can close this tab.'

    def start_oauth_flow(self) -> Optional[dict]:
        threading.Thread(
            target=lambda: self._app.run(port=self.port),
            daemon=True
        ).start()

        self.browser.open(conf.auth_url)
        print('Waiting for user authorization...')

        while self._auth_code is None:
            time.sleep(0.5)

        tokens = self.client.exchange_code_for_token(self._auth_code)
        if tokens:
            self.token_store.save_tokens(tokens)
        return tokens

    def get_valid_access_token(self) -> str:
        if time.time() >= self.token_store.get_expiry():
            print('Access token expired — refreshing...')
            refreshed = self.client.refresh_access_token(
                self.token_store.get_refresh_token())
            if refreshed:
                self.token_store.save_tokens(refreshed)
        return self.token_store.get_access_token()
# === Decorator for instance methods ===


def with_valid_token(oauth_attr: str):
    """
    oauth_attr: name of the attribute on `self` holding an OAuthService.
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            oauth_service: OAuthService = getattr(self, oauth_attr)
            headers = {
                'Authorization': (
                    f'Bearer {oauth_service.get_valid_access_token()}'
                )
            }
            return func(self, *args, headers=headers, **kwargs)
        return wrapper
    return decorator


# === API Client ===
class APIClient:
    def __init__(self, oauth_service: OAuthService) -> None:
        self.oauth_service = oauth_service

    @with_valid_token('oauth_service')
    def get_my_resumes(self, *, headers=None):
        url = f'{conf.API_BASE_URL}/resumes/mine'
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    @with_valid_token('oauth_service')
    def get_recommended_vacancies(self, resume_id: str, *, headers=None):
        url = f'{conf.API_BASE_URL}/resumes/{resume_id}/similar_vacancies'
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


# === Main Execution ===
if __name__ == '__main__':
    token_store = InMemoryTokenStore()
    oauth_client = RequestsOAuthClient()
    browser = WebBrowserLauncher()
    oauth_service = OAuthService(
        oauth_client,
        token_store,
        browser,
        port=conf.PORT
    )

    api_client = APIClient(oauth_service)

    oauth_service.start_oauth_flow()

    resumes = api_client.get_my_resumes()
    if not resumes.get('items'):
        print('No resumes found.')
    else:
        resume_id = resumes['items'][0]['id']
        print(f'Using resume ID: {resume_id}')

        vacancies = api_client.get_recommended_vacancies(resume_id)
        for vacancy in vacancies.get('items', []):
            print(vacancy['name'], '-', vacancy['alternate_url'])
