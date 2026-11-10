from skillmapper.api.schemas.generics import ItemsResponse
from skillmapper.api.schemas.resume import Resume
from skillmapper.api.schemas.vacancy import Vacancy
from skillmapper.infrastructure.http.client import HttpClient


class APIClient:
    def __init__(self, http: HttpClient):
        self._http = http

    def get_my_resumes(self) -> list[Resume]:
        response = self._http.get("/resumes/mine")
        response.raise_for_status()
        return ItemsResponse[Resume].model_validate(response.json()).items

    def get_recommended_vacancies(self, resume_id: str) -> list[Vacancy]:
        response = self._http.get(f"/resumes/{resume_id}/similar_vacancies")
        response.raise_for_status()
        return ItemsResponse[Vacancy].model_validate(response.json()).items
