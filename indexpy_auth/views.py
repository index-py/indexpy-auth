import abc
from http import HTTPStatus

from indexpy import Body, Header, HttpView
from indexpy.openapi import describe_response


class LogInAndOut(HttpView, abc.ABC):
    @describe_response(
        HTTPStatus.CREATED,
        headers={
            "Set-Token": {
                "description": "Token",
                "schema": {"type": "string"},
            },
        },
    )
    async def post(self, username: str = Body(...), password: str = Body(...)):
        token = await self.login(username, password)
        # https://datatracker.ietf.org/doc/html/rfc6750#section-4
        return {"access_token": token, "token_type": "Bearer"}, 201

    @abc.abstractmethod
    async def login(self, username: str, password: str) -> str:
        raise NotImplementedError

    @describe_response(HTTPStatus.RESET_CONTENT)
    async def delete(self, token: str = Header(...)):
        await self.logout(token)
        return {"message": HTTPStatus.RESET_CONTENT.description}, 205

    @abc.abstractmethod
    async def logout(self, token: str) -> None:
        raise NotImplementedError
