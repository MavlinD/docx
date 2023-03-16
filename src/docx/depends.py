from enum import Enum

from fastapi import Form, UploadFile, File, HTTPException, Depends
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from starlette import status

from src.docx.config import config
from src.docx.helpers.security import decode_jwt
from src.docx.schemas import DocxCreate, DocxUpdate, token_description, Token


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
    log.trace(token)
    jwt = Token(token=token)
    await decode_jwt(
        payload=jwt,
        audience=Audience.UPDATE.value,
    )
    return True


async def check_content_type(
    file: UploadFile,
) -> UploadFile:
    """Зависимость"""
    # log.debug(file.size)
    if file.content_type not in config.content_type_white_list.values():
        raise HTTPException(
            detail=f"Тип файла не разрешен: {file.content_type}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return file


async def check_file_size(
    file: UploadFile,
) -> UploadFile:
    """Зависимость"""
    # log.debug(file.size)
    if file.size and file.size > config.FILE_MAX_SIZE * 1024 * 1024:
        raise HTTPException(
            detail="Файл слишком большой, {:.2f} Mb".format(file.size / 1024 / 1024),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return file


async def check_file_condition(
    file: UploadFile = File(  # noqa
        ...,
        description=f"Разрешены следующие типы файлов: __{', '.join(config.content_type_white_list.keys())}__<br>"
        f"Максимальный размер загружаемого файла: **{config.FILE_MAX_SIZE}** Mb",
    )
) -> bool:
    """Зависимость"""
    Depends(check_content_type)
    Depends(check_file_size)

    return True
