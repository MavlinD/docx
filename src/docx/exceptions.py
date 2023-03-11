from enum import Enum
from typing import Any, Dict, Union

from fastapi import HTTPException
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from starlette import status


class ErrorModel(BaseModel):
    detail: Union[str, dict[str, str]]


class ErrorCodeReasonModel(BaseModel):
    code: str
    reason: str


OpenAPIResponseType = Dict[Union[int, str], Dict[str, Any]]

none_message_response: OpenAPIResponseType = {
    status.HTTP_202_ACCEPTED: {"content": None},
}


class ErrorCodeLocal(str, Enum):
    TOKEN_EXPIRE = "Срок действия токена истёк."
    TOKEN_AUD_FAIL = "Некорректная аудиенция токена."
    TOKEN_AUD_NOT_FOUND = "Требуемая аудиенция токена не найдена."
    TOKEN_AUD_NOT_ALLOW = "Запрошенная аудиенция токена не разрешена."


class FastAPIDocxException(HTTPException):
    def __init__(self) -> None:
        self.detail: str = "Некорректный запрос"
        self.status_code: int = status.HTTP_400_BAD_REQUEST


class InvalidVerifyToken(FastAPIDocxException):
    def __init__(self, msg: Exception | str | None = None) -> None:
        self.detail = f"Токен не валиден: {msg}"
        self.status_code = status.HTTP_403_FORBIDDEN
