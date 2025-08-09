import urllib.parse

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseModel):
    client_id: str
    client_secret: str
    application_number: int
    base_auth_url: str = "https://hh.ru/oauth/authorize"
    token_url: str = "https://api.hh.ru/token"
    redirect_scheme: str = "http"
    redirect_host: str = "localhost"
    redirect_port: int = 8080
    redirect_path: str = "/callback"

    @property
    def auth_payload(self) -> dict:
        return {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }

    @property
    def auth_url(self) -> str:
        return (
            f"{self.base_auth_url}?{urllib.parse.urlencode(self.auth_payload)}"
        )

    def authorization_code_payload(self, auth_code: str) -> dict:
        return {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }

    @property
    def redirect_uri(self) -> str:
        parts = (
            self.redirect_scheme,
            f"{self.redirect_host}:{self.redirect_port}",
            self.redirect_path,
            "",
            "",
            "",
        )
        return urllib.parse.urlunparse(parts)

    def refresh_token_payload(self, refresh_token: str) -> dict:
        return {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }


class HttpSettings(BaseModel):
    timeout: float = 15.0


class ApiSettings(BaseModel):
    base_url: str = "https://api.hh.ru"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    oauth: OAuthSettings
    http: HttpSettings = HttpSettings()
    api: ApiSettings = ApiSettings()
