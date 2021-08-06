from __future__ import annotations

import abc
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Dict, Mapping, Tuple, TypeVar, Union

from indexpy import request
from indexpy.openapi import describe_extra_docs

T_Response = TypeVar("T_Response")

DictResponse = Union[
    Tuple[Dict[str, Any]],
    Tuple[Dict[str, Any], int],
    Tuple[Dict[str, Any], int, Mapping[str, str]],
]


UnAuthorizedResp: DictResponse = (
    {"message": HTTPStatus.UNAUTHORIZED.description},
    HTTPStatus.UNAUTHORIZED,
    {"WWW-Authenticate": "Bearer"},
)


class NeedAuthentication(metaclass=abc.ABCMeta):
    def __init__(self, endpoint: Callable[[], Awaitable[T_Response]]) -> None:
        self.endpoint = endpoint
        describe_extra_docs(
            endpoint,
            {
                # "parameters": [
                #     {
                #         "name": "Authorization",
                #         "in": "header",
                #         "description": "token to be passed as a header",
                #         "required": "true",
                #         "schema": {
                #             "type": "string",
                #         },
                #         "example": "Bearer YOUR-TOKEN",
                #     }
                # ],
                "responses": {
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                        "headers": {
                            "WWW-Authenticate": {
                                "description": "Bearer token",
                                "schema": {"type": "string"},
                            }
                        },
                    },
                },
            },
        )

    async def __call__(self) -> T_Response | DictResponse:
        authorization = request.headers.get("Authorization", None)
        if authorization is None:
            return UnAuthorizedResp
        type, token = authorization.strip().split(" ", maxsplit=1)
        if type != "Bearer":
            return UnAuthorizedResp
        if not await self.authenticate(token):
            return UnAuthorizedResp
        return await self.endpoint()

    @abc.abstractmethod
    async def authenticate(self, token: str) -> bool:
        raise NotImplementedError
