from skillmapper.oauth.token_provider import OAuthTokenProvider


class Store:
    def __init__(self, data):
        self.data = data
        self.saved = []

    def load_tokens(self):
        return self.data

    def save_tokens(self, tokens):
        self.data = dict(tokens)
        self.saved.append(dict(tokens))


class Client:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def refresh_access_token(self, token):
        self.calls += 1
        return self.response


def test_refresh_keeps_existing_refresh_token():
    store = Store(
        {"access_token": "old", "refresh_token": "r1", "expires_at": 10}
    )
    client = Client({"access_token": "new", "expires_in": 3600})
    provider = OAuthTokenProvider(
        client, store, clock=lambda: 100, expiry_skew=0
    )
    assert provider.get_access_token() == "new"
    assert store.data["refresh_token"] == "r1"
    assert client.calls == 1


def test_valid_token_is_reused():
    store = Store(
        {"access_token": "valid", "refresh_token": "r1", "expires_at": 500}
    )
    client = Client({})
    provider = OAuthTokenProvider(
        client, store, clock=lambda: 100, expiry_skew=0
    )
    assert provider.get_access_token() == "valid"
    assert client.calls == 0
