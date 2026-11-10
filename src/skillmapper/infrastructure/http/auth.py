from requests import PreparedRequest
from requests.auth import AuthBase

from skillmapper.oauth.protocols import AccessTokenProvider


class BearerTokenAuth(AuthBase):
    def __init__(self, provider: AccessTokenProvider):
        self._provider = provider

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = (
            f"Bearer {self._provider.get_access_token()}"
        )
        return request
