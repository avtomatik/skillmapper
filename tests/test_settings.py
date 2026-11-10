from skillmapper.config.settings import OAuthSettings


def test_redirect_and_authorization_url():
    settings = OAuthSettings(
        client_id="id", client_secret="secret", application_number=5
    )
    assert settings.redirect_uri == "http://localhost:8080/callback"
    url = settings.authorization_url("state123")
    assert "client_id=id" in url and "state=state123" in url
