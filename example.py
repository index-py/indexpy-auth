from typing import Annotated
from indexpy import Index, Routes, PlainTextResponse
from indexpy.openapi import OpenAPI

from indexpy_auth.middlewares import NeedAuthentication

app = Index(debug=True)

docs = OpenAPI(security_schemes=NeedAuthentication.security_scheme)

app.router << "/docs" // docs.routes


class AuthMiddleware(NeedAuthentication):
    async def authenticate(self, token: str) -> bool:
        return token == "qwertyuiopasdfghjklzxcvbnm"


routes = Routes(http_middlewares=[AuthMiddleware])


@routes.http.get("/")
async def index() -> Annotated[str, PlainTextResponse[200]]:
    """
    index
    """
    return "Hello, world!"


@routes.http.get("/user")
async def user() -> Annotated[str, PlainTextResponse[200]]:
    """
    user
    """
    return "Hello, user!"


app.router << routes
