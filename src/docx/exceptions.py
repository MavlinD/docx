from fastapi import HTTPException
from logrich.logger_ import log  # noqa
from starlette import status


class FastAPIUsersException(HTTPException):
    def __init__(self) -> None:
        self.detail: str = "Некорректный запрос"
        self.status_code: int = status.HTTP_400_BAD_REQUEST


class InvalidVerifyToken(FastAPIUsersException):
    def __init__(self, msg: Exception | str | None = None) -> None:
        self.detail = f"Токен не валиден: {msg}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
