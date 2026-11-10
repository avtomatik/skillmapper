from requests import Request

from skillmapper.infrastructure.http.auth import BearerTokenAuth


class Provider:
    def get_access_token(self):
        return "abc"


def test_bearer_header_added():
    request = Request("GET", "https://api.hh.ru/resumes/mine").prepare()
    assert (
        BearerTokenAuth(Provider())(request).headers["Authorization"]
        == "Bearer abc"
    )
