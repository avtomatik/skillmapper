import requests

from api.decorators import with_valid_token
from api.schemas.generics import ItemsResponse
from api.schemas.resume import Resume
from api.schemas.vacancy import Vacancy
from config.settings import Settings
from oauth.service import OAuthService


class APIClient:
    def __init__(
        self, settings: Settings, oauth_service: OAuthService
    ) -> None:
        self.settings = settings
        self.oauth_service = oauth_service

    @with_valid_token("oauth_service")
    def get_my_resumes(self, *, headers=None) -> list[Resume]:
        url = f"{self.settings.api.base_url}/resumes/mine"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        parsed = ItemsResponse[Resume].model_validate(response.json())
        return parsed.items

    @with_valid_token("oauth_service")
    def get_recommended_vacancies(
        self, resume_id: str, *, headers=None
    ) -> list[Vacancy]:
        url = f"{self.settings.api.base_url}/resumes/{resume_id}/similar_vacancies"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        parsed = ItemsResponse[Vacancy].model_validate(response.json())
        return parsed.items
