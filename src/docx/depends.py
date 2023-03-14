from enum import Enum

from fastapi import Body, Form
from logrich.logger_ import log  # noqa
from pydantic import Field

from src.docx.config import config
from src.docx.helpers.security import decode_jwt
from src.docx.schemas import DocxCreate, DocxUpdate


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
        description=f"JWT подписанный асинхронным алгоритмом из списка {config.ALGORITHMS_WHITE_LIST},"
        "<br>при этом аудиенция токена должна соотвествовать аудиенции конечной точки."
        "<br>Издатель должен её включить в токен перед запросом.",
        # max_length=55,
    ),
    # token: str
    # | None = Body(..., description=f"jhgjhg-{config.TEMPLATE_MAX_LENGTH}")
) -> bool:
    """Зависимость, авторизует запрос на обновление шаблона"""
    log.debug(token)
    jwt = DocxUpdate(token=token)
    log.trace(jwt)
    # return True
    await decode_jwt(
        # payload=token,
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
