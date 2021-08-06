from indexpy import Index, Routes
from indexpy.openapi import OpenAPI
from indexpy.openapi.functions import describe_extra_docs

from indexpy_auth.middlewares import NeedAuthentication

app = Index(debug=True)

docs = OpenAPI("", "", "")
docs.openapi["components"].setdefault("securitySchemes", {}).update(
    {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    }
)

app.router << "/docs" // docs.routes


class AuthMiddleware(NeedAuthentication):
    def __init__(self, endpoint):
        super().__init__(endpoint)
        describe_extra_docs(endpoint, {"security": [{"BearerAuth": []}]})

    async def authenticate(self, token: str) -> bool:
        return True


routes = Routes(http_middlewares=[AuthMiddleware])


@routes.http.get("/")
async def index():
    """
    index
    """
    return "Hello, world!"


@routes.http.get("/user")
async def user():
    """
    user
    """
    return "Hello, user!"


app.router << routes
