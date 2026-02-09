from api.client import APIClient
from config.conf import conf
from oauth.browser import WebBrowserLauncher
from oauth.clients import RequestsOAuthClient
from oauth.service import OAuthService
from oauth.token_store import InMemoryTokenStore

if __name__ == "__main__":
    token_store = InMemoryTokenStore()
    oauth_client = RequestsOAuthClient()
    browser = WebBrowserLauncher()
    oauth_service = OAuthService(
        oauth_client, token_store, browser, port=conf.PORT
    )

    api_client = APIClient(oauth_service)

    oauth_service.start_oauth_flow()

    resumes = api_client.get_my_resumes()
    if not resumes:
        print("No resumes found.")
    else:
        resume_id = resumes[0].id
        print(f"Using resume ID: {resume_id}")

        vacancies = api_client.get_recommended_vacancies(resume_id)
        for vacancy in vacancies:
            print(vacancy.name, "-", vacancy.alternate_url)
