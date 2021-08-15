from __future__ import annotations

import abc
from http import HTTPStatus
from typing import Awaitable, Callable, Generic, TypeVar

from indexpy import request, HTTPException, status
from indexpy.openapi import describe_extra_docs, describe_response

T_Response = TypeVar("T_Response")


class NeedAuthentication(Generic[T_Response], metaclass=abc.ABCMeta):
    security_scheme = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    def __init__(self, endpoint: Callable[[], Awaitable[T_Response]]) -> None:
        self.endpoint = endpoint
        describe_extra_docs(endpoint, {"security": [{"BearerAuth": []}]})

    @describe_response(
        "401",
        content={
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                    },
                }
            }
        },
        headers={
            "WWW-Authenticate": {
                "description": "Bearer token",
                "schema": {"type": "string"},
            }
        },
    )
    async def __call__(self) -> T_Response:
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
        return await self.endpoint()

    @abc.abstractmethod
    async def authenticate(self, token: str) -> bool:
        raise NotImplementedError
