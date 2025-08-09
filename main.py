from api.client import APIClient
from config.settings import Settings
from oauth.browser import WebBrowserLauncher
from oauth.clients import RequestsOAuthClient
from oauth.service import OAuthService
from oauth.token_store import InMemoryTokenStore


def create_api_client(settings: Settings) -> APIClient:
    token_store = InMemoryTokenStore()
    oauth_client = RequestsOAuthClient(settings)
    browser = WebBrowserLauncher()
    oauth_service = OAuthService(settings, oauth_client, token_store, browser)
    oauth_service.start_oauth_flow()
    return APIClient(settings, oauth_service)


def print_recommended_vacancies(api_client: APIClient):
    resumes = api_client.get_my_resumes()
    if not resumes:
        print("No resumes found.")
        return
    for resume in resumes:
        print(f"Using resume ID: {resume.id}")
        vacancies = api_client.get_recommended_vacancies(resume.id)
        for vacancy in vacancies:
            print(f"{resume.id}: {vacancy.name} -> {vacancy.snippet}.")


def main() -> None:
    settings = Settings()
    api_client = create_api_client(settings)
    print_recommended_vacancies(api_client)


if __name__ == "__main__":
    main()
