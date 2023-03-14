from enum import Enum

from logrich.logger_ import log  # noqa

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


async def check_update_access(payload: DocxUpdate) -> bool:
    """Зависимость, авторизует запрос на обновление шаблона"""
    await decode_jwt(
        payload=payload,
        audience=Audience.UPDATE.value,
    )
    return True
