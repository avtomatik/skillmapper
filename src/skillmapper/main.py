from skillmapper.api.client import APIClient
from skillmapper.config.settings import Settings
from skillmapper.infrastructure.http.auth import BearerTokenAuth
from skillmapper.infrastructure.http.client import HttpClient
from skillmapper.oauth.browser import WebBrowserLauncher
from skillmapper.oauth.clients import RequestsOAuthClient
from skillmapper.oauth.exceptions import AuthorizationRequired
from skillmapper.oauth.flow import OAuthFlow
from skillmapper.oauth.token_provider import OAuthTokenProvider
from skillmapper.oauth.token_store import JsonTokenStore


def print_recommended_vacancies(api: APIClient) -> None:
    resumes = api.get_my_resumes()
    if not resumes:
        print("No resumes found.")
        return
    for resume in resumes:
        print(f"Using resume ID: {resume.id}")
        vacancies = api.get_recommended_vacancies(resume.id)
        for vacancy in vacancies:
            snippet = (
                vacancy.snippet.requirement or vacancy.snippet.responsibility
            )
            print(f"{resume.id}: {vacancy.name} -> {snippet}")


def main() -> None:
    settings = Settings()
    oauth_client = RequestsOAuthClient(
        settings.oauth, timeout=settings.http.timeout
    )
    try:
        provider = OAuthTokenProvider(
            oauth_client, JsonTokenStore(settings.token_store.path)
        )
        try:
            provider.get_access_token()
        except AuthorizationRequired:
            OAuthFlow(
                settings.oauth, oauth_client, WebBrowserLauncher(), provider
            ).authorize()
        with HttpClient(
            settings.api.base_url,
            timeout=settings.http.timeout,
            auth=BearerTokenAuth(provider),
        ) as http:
            print_recommended_vacancies(APIClient(http))
    finally:
        oauth_client.close()


if __name__ == "__main__":
    main()
