from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http.cookie import parse_cookie
from graphql_jwt.utils import get_credentials 
from graphql_jwt.shortcuts import get_user_by_token
from urllib.parse import parse_qs
@database_sync_to_async
def get_user(token):
    if token is None:
        return AnonymousUser()
    return get_user_by_token(token)


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        # cookie based authentication
        # cookie = next((x[1] for x in scope["headers"] if x[0] == b"cookie"), None)
        # token = parse_cookie(cookie.decode("latin1"))

        # query string based authentication
        qs = scope["query_string"]
        token = parse_qs(qs.decode("utf8"))
        if token.get("jwt-token", False):
            scope['user'] = await get_user(token["jwt-token"][0])
        else:
            scope['user'] = AnonymousUser()


        return await self.app(scope, receive, send)