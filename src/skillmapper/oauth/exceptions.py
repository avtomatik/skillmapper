class OAuthError(RuntimeError):
    """Base OAuth failure."""


class AuthorizationRequired(OAuthError):
    """Interactive authorization is required."""


class TokenRefreshError(OAuthError):
    """Token refresh failed."""
