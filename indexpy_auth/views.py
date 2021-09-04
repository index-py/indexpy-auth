import abc
from http import HTTPStatus
from typing import Any

from indexpy import Body, HttpView, JSONResponse, Query
from pydantic.main import create_model
from typing_extensions import Annotated, Literal


class LogInAndOut(HttpView, abc.ABC):
    async def post(
        self, username: str = Body(...), password: str = Body(...)
    ) -> Annotated[
        Any,
        JSONResponse[
            201,
            {},
            create_model(
                "CreatedToken",
                access_token=(str, ...),
                token_type=(Literal["Bearer"], "Bearer"),
            ),
        ],
    ]:
        token = await self.login(username, password)
        # https://datatracker.ietf.org/doc/html/rfc6750#section-4
        return {"access_token": token, "token_type": "Bearer"}, 201

    @abc.abstractmethod
    async def login(self, username: str, password: str) -> str:
        raise NotImplementedError

    async def delete(
        self, token: str = Query(...)
    ) -> Annotated[
        Any,
        JSONResponse[205, {}, create_model("Message", message=(str, ...))],
    ]:
        await self.logout(token)
        return {"message": HTTPStatus.RESET_CONTENT.description}, 205

    @abc.abstractmethod
    async def logout(self, token: str) -> None:
        raise NotImplementedError
