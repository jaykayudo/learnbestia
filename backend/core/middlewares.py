from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


@database_sync_to_async
def get_user_from_token(_token):
    try:
        instance = JWTAuthentication()
        token = instance.get_validated_token(_token)
        return instance.get_user(token)
    except TokenError:
        return AnonymousUser()
    except Exception:
        return AnonymousUser()


class TokenGetMiddleware:
    """
    Middleware for websocket connection authentication 
    using restframework token authentication
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        params = parse_qs(scope["query_string"].decode())
        if "token" in params:
            try:
                # token check code written here
                token = params["token"][0]
                user = await get_user_from_token(token.encode())
                scope["user"] = user
            except Exception:
                pass
        return await self.inner(scope, receive, send)


def TokenGetMiddlewareStack(inner):
    return TokenGetMiddleware(AuthMiddlewareStack(inner))
