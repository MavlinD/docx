import dataclasses
from enum import Enum
from typing import Any, Callable, Iterable

from fastapi import UploadFile, File
from logrich.logger_ import log  # noqa

from src.docx.config import config

from src.docx.schemas import file_description, JWT
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.docx.exceptions import ErrorModel, ErrorCodeLocal, FileIsTooLarge, FileExtensionReject


class Audience(str, Enum):
    READ = "docx-read"
    CREATE = "docx-create"
    UPDATE = "docx-update"
    DELETE = "docx-delete"
    SUPER = "docx-super"


@dataclasses.dataclass
class AudienceCompose:
    READ: Iterable[str] = Audience.READ.value, Audience.SUPER.value
    CREATE: Iterable[str] = Audience.CREATE.value, Audience.SUPER.value
    UPDATE: Iterable[str] = Audience.UPDATE.value, Audience.SUPER.value
    DELETE: Iterable[str] = Audience.DELETE.value, Audience.SUPER.value


class JWTBearer(HTTPBearer):
    """For OpenAPI"""

    # https://testdriven.io/blog/fastapi-jwt-auth/
    def __init__(self, audience: str | Iterable[str] | None = None, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.audience = audience

    async def __call__(self, request: Request) -> Any:
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearer, self).__call__(
            request
        )
        # log.debug(credentials)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token = JWT(token=credentials.credentials)
            # log.debug(token.token)
            token.audience = self.audience
            # log.info(self.audience)
            token.set_issuer()
            payload = await token.decode_jwt
            # log.debug("", o=payload)
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


def file_checker_wrapper(
    content_type: dict | None = None, file_max_size: float | None = None
) -> Callable:
    if not file_max_size:
        file_max_size = config.FILE_MAX_SIZE
    if not content_type:
        content_type = config.content_type_white_list

    def content_checker(
        file: UploadFile = File(
            ...,
            description=file_description(content_type=content_type, file_max_size=file_max_size),
        ),
    ) -> UploadFile:
        if file.size and (file.size > config.FILE_MAX_SIZE * 1024 * 1024):
            raise FileIsTooLarge(file=file)

        if file.content_type not in config.content_type_white_list.values():
            raise FileExtensionReject(file=file)

        return file

    return content_checker


# Исключения для JWT
JWT_STATUS_HTTP_403_FORBIDDEN = {
    "model": ErrorModel,
    "content": {
        "application/json": {
            "examples": {
                ErrorCodeLocal.TOKEN_EXPIRE: {
                    "summary": "Срок действия токена вышел.",
                    "value": {"detail": ErrorCodeLocal.TOKEN_EXPIRE},
                },
                ErrorCodeLocal.TOKEN_AUD_NOT_FOUND: {
                    "summary": "Действие требует определённой аудиенции.",
                    "value": {"detail": ErrorCodeLocal.TOKEN_AUD_NOT_FOUND},
                },
                ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT: {
                    "summary": "Структура токена не валидна.",
                    "value": {"detail": ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT},
                },
                ErrorCodeLocal.TOKEN_ALGORITHM_NOT_FOUND: {
                    "summary": "Алгоритм токена неизвестен.",
                    "value": {"detail": ErrorCodeLocal.TOKEN_ALGORITHM_NOT_FOUND},
                },
            }
        }
    },
}

JWT_HTTP_400_BAD_REQUEST = {
    "model": ErrorModel,
    "content": {
        "application/json": {
            "examples": {
                ErrorCodeLocal.TOKEN_NSP_NOT_FOUND: {
                    "summary": "Токен должен содержать поле NSP - папку пользователя.",
                    "value": {"detail": ErrorCodeLocal.TOKEN_NSP_NOT_FOUND},
                },
            }
        }
    },
}

FILE_STATUS_HTTP_404_NOT_FOUND = {
    "model": ErrorModel,
    "content": {
        "application/json": {
            "examples": {
                ErrorCodeLocal.TEMPLATE_NOT_EXIST: {
                    "summary": "Указанный файл/шаблон не найден.",
                    "value": {"detail": ErrorCodeLocal.TEMPLATE_NOT_EXIST},
                },
            }
        }
    },
}
