from enum import Enum

from fastapi import Body, Form, Depends
from logrich.logger_ import log  # noqa
from pydantic import Field

from src.docx.config import config
from src.docx.helpers.security import decode_jwt
from src.docx.schemas import DocxCreate, DocxUpdate, JWToken, token_description


class Audience(str, Enum):
    CREATE = "docx-create"
    UPDATE = "docx-update"


async def check_create_access(payload: DocxCreate) -> bool:
    """Зависимость, авторизует запрос на создание файла"""
    await decode_jwt(
        payload=payload,
        audience=Audience.CREATE.value,
    )
    return True


async def check_update_access(
    token: str = Form(
        ...,
        description=token_description,
        # max_length=100
    ),
) -> bool:
    """Зависимость, авторизует запрос на обновление шаблона"""
    # log.trace(token)
    jwt = DocxUpdate(token=token)
    await decode_jwt(
        payload=jwt,
        audience=Audience.UPDATE.value,
    )
    return True


# async def check_update_access(token: Field) -> bool:
#     """Зависимость, авторизует запрос на обновление шаблона"""
#     await decode_jwt(
#         payload=token,
#         audience=Audience.UPDATE.value,
#     )
#     return True
