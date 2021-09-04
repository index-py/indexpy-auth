from __future__ import annotations

import abc
from http import HTTPStatus
from typing import Awaitable, Callable, Generic, TypeVar

from indexpy import HTTPException, JSONResponse, request, status
from indexpy.openapi import describe_extra_docs
from pydantic import BaseModel
from typing_extensions import Annotated

T_Response = TypeVar("T_Response")


class Message(BaseModel):
    message: str


class NeedAuthentication(Generic[T_Response], metaclass=abc.ABCMeta):
    security_scheme = {"BearerAuth": {"type": "http", "scheme": "bearer"}}

    def __init__(self, endpoint: Callable[[], Awaitable[T_Response]]) -> None:
        self.endpoint = endpoint
        describe_extra_docs(endpoint, {"security": [{"BearerAuth": []}]})

    async def __call__(
        self,
    ) -> Annotated[
        T_Response,
        JSONResponse[
            401,
            {
                "WWW-Authenticate": {
                    "description": "Bearer token",
                    "schema": {"type": "string"},
                }
            },
            Message,
        ],
    ]:
        authorization = request.headers.get("Authorization", None)
        if authorization is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": HTTPStatus.UNAUTHORIZED.description},
            )
        type, token = authorization.strip().split(" ", maxsplit=1)
        if type != "Bearer":
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": HTTPStatus.UNAUTHORIZED.description},
            )
        if not await self.authenticate(token):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": HTTPStatus.UNAUTHORIZED.description},
            )
        request.state.authorization_token = token
        return await self.endpoint()

    @abc.abstractmethod
    async def authenticate(self, token: str) -> bool:
        raise NotImplementedError
