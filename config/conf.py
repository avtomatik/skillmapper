import urllib.parse

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CLIENT_ID: str = (
        "00000000000000000000AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )
    CLIENT_SECRET: str = (
        "0000000000000000AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )
    APPLICATION_NUMBER: str = "11111"
    REDIRECT_SCHEME: str = "http"
    REDIRECT_HOST: str = "localhost"
    PORT: str = "8080"
    REDIRECT_PATH: str = "/callback"

    AUTH_BASE_URL: str = "https://hh.ru/oauth/authorize"
    TOKEN_URL: str = "https://api.hh.ru/token"
    API_BASE_URL: str = "https://api.hh.ru"

    @property
    def redirect_uri(self) -> str:
        netloc = f"{self.REDIRECT_HOST}:{self.PORT}"
        parts = (self.REDIRECT_SCHEME, netloc, self.REDIRECT_PATH, "", "", "")
        return urllib.parse.urlunparse(parts)

    @property
    def auth_payload(self) -> dict:
        return {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.redirect_uri,
        }

    @property
    def auth_url(self) -> str:
        return (
            f"{self.AUTH_BASE_URL}?{urllib.parse.urlencode(self.auth_payload)}"
        )

    def authorization_code_payload(self, auth_code: str) -> dict:
        return {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": self.redirect_uri,
        }

    def refresh_token_payload(self, refresh_token: str) -> dict:
        return {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
        }

    class Config(ConfigDict):
        env_file = ".env"


conf = Settings()
