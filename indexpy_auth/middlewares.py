from __future__ import annotations

import abc
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Dict, Mapping, Tuple, TypeVar, Union

from indexpy import request

T_Response = TypeVar("T_Response")

DictResponse = Union[
    Tuple[Dict[str, Any]],
    Tuple[Dict[str, Any], int],
    Tuple[Dict[str, Any], int, Mapping[str, str]],
]


class NeedAuthentication(metaclass=abc.ABCMeta):
    def __init__(self, endpoint: Callable[[], Awaitable[T_Response]]) -> None:
        self.endpoint = endpoint

    async def __call__(self) -> T_Response | DictResponse:
        authorization = request.headers.get("Authorization", None)
        if authorization is None:
            return (
                {"message": HTTPStatus.UNAUTHORIZED.description},
                HTTPStatus.UNAUTHORIZED,
                {"WWW-Authenticate": "Bearer"},
            )
        type, token = authorization.strip().split(" ", maxsplit=1)
        if type != "Bearer":
            return (
                {"message": HTTPStatus.UNAUTHORIZED.description},
                HTTPStatus.UNAUTHORIZED,
                {"WWW-Authenticate": "Bearer"},
            )
        if not self.authenticate(token):
            return (
                {"message": HTTPStatus.FORBIDDEN.description},
                HTTPStatus.FORBIDDEN,
            )
        return await self.endpoint()

    @abc.abstractmethod
    async def authenticate(self, token: str) -> bool:
        raise NotImplementedError
