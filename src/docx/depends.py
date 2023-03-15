from enum import Enum

from fastapi import Form, UploadFile, File, HTTPException
from logrich.logger_ import log  # noqa
from starlette import status

from src.docx.config import config
from src.docx.helpers.security import decode_jwt
from src.docx.schemas import DocxCreate, DocxUpdate, token_description


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


async def get_file(
    file: UploadFile = File(
        ...,
        description=f"Максимальный размер загружаемого файла: **{config.FILE_MAX_SIZE}** Mb",
    )
    # ) -> bool:
) -> UploadFile:
    """Зависимость"""
    # log.debug(file.size)
    if file.size and file.size > config.FILE_MAX_SIZE * 1024 * 1024:
        raise HTTPException(
            detail="Файл слишком большой, {:.2f} Mb".format(file.size / 1024 / 1024),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return file
