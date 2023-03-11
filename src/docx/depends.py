from logrich.logger_ import log  # noqa

from src.docx.helpers.security import decode_jwt
from src.docx.schemas import DocxCreate


async def check_create_access(payload: DocxCreate) -> bool:
    """Зависимость, авторизует запрос на создание файла"""
    await decode_jwt(
        payload=payload,
        audience="create",
    )
    return True


async def check_update_access(payload: DocxCreate) -> bool:
    """Зависимость, авторизует запрос на обновление шаблона"""
    await decode_jwt(
        payload=payload,
        audience="update",
    )
    return True
