import requests

from api.decorators import with_valid_token
from api.schemas.common import ItemsResponse
from api.schemas.resume import Resume
from api.schemas.vacancy import Vacancy
from config.conf import conf
from oauth.service import OAuthService


class APIClient:
    def __init__(self, oauth_service: OAuthService) -> None:
        self.oauth_service = oauth_service

    @with_valid_token("oauth_service")
    def get_my_resumes(self, *, headers=None) -> list[Resume]:
        url = f"{conf.API_BASE_URL}/resumes/mine"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        parsed = ItemsResponse[Resume].model_validate(data)
        return parsed.items

    @with_valid_token("oauth_service")
    def get_recommended_vacancies(
        self, resume_id: str, *, headers=None
    ) -> list[Vacancy]:
        url = f"{conf.API_BASE_URL}/resumes/{resume_id}/similar_vacancies"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        parsed = ItemsResponse[Vacancy].model_validate(data)
        return parsed.items
