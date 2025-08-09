from functools import wraps
from typing import Any, Callable

from oauth.service import OAuthService


def with_valid_token(oauth_attr: str):
    """
    oauth_attr: name of the attribute on `self` holding an OAuthService.
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            oauth_service: OAuthService = getattr(self, oauth_attr)
            headers = {
                'Authorization': (
                    f'Bearer {oauth_service.get_valid_access_token()}'
                )
            }
            return func(self, *args, headers=headers, **kwargs)
        return wrapper
    return decorator
