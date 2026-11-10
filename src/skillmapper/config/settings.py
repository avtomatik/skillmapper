from pathlib import Path
from urllib.parse import urlencode

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseModel):
    client_id: str
    client_secret: SecretStr
    application_number: int
    auth_url: str = "https://hh.ru/oauth/authorize"
    token_url: str = "https://api.hh.ru/token"
    redirect_scheme: str = "http"
    redirect_host: str = "localhost"
    redirect_port: int = 8080
    redirect_path: str = "/callback"
    authorization_timeout: float = 180.0

    @property
    def redirect_uri(self) -> str:
        return (
            f"{self.redirect_scheme}://"
            f"{self.redirect_host}:"
            f"{self.redirect_port}"
            f"{self.redirect_path}"
        )

    def authorization_url(self, state: str) -> str:
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "state": state,
            }
        )
        return f"{self.auth_url}{'&' if '?' in self.auth_url else '?'}{query}"


class HttpSettings(BaseModel):
    timeout: float = 15.0


class ApiSettings(BaseModel):
    base_url: str = "https://api.hh.ru"


class TokenStoreSettings(BaseModel):
    path: Path = Path(".state/tokens.json")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    oauth: OAuthSettings
    http: HttpSettings = HttpSettings()
    api: ApiSettings = ApiSettings()
    token_store: TokenStoreSettings = TokenStoreSettings()
