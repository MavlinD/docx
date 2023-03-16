from enum import Enum
from typing import Any

from fastapi import Form, UploadFile, File, HTTPException, Depends
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from starlette import status

from src.docx.config import config
from src.docx.helpers.security import decode_jwt
from src.docx.schemas import (
    DocxCreate,
    DocxUpdate,
    token_description,
    file_description,
    bool_description,
    JWToken,
)


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
    jwt = JWToken(token=token)
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


def file_checker_wrapper(content_type: dict, file_max_size: float) -> Any:
    """Обёртка над зависисмостью."""

    # https://stackoverflow.com/questions/65504438/how-to-add-both-file-and-json-body-in-a-fastapi-post-request
    class FixedContentQueryChecker:
        def __init__(self, content_type: dict, file_max_size: float):
            self.content_type = content_type
            self.file_max_size = file_max_size

        def __call__(
            self,
            file: UploadFile = File(
                ...,
                description=file_description(
                    content_type=content_type, file_max_size=file_max_size
                ),
            ),
            token: str = Form(..., description=token_description),
            filename: str = Form(
                None,
                description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
                "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
            ),
            replace_if_exist: bool = Form(
                False, description=f"Заменить шаблон, если он существует. {bool_description}"
            ),
        ) -> DocxUpdate:
            if file.size and file.size > config.FILE_MAX_SIZE * 1024 * 1024:
                raise HTTPException(
                    detail="Файл слишком большой, {:.2f} Mb".format(file.size / 1024 / 1024),
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            if file.content_type not in config.content_type_white_list.values():
                raise HTTPException(
                    detail=f"Тип файла не разрешен: {file.content_type}",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            return DocxUpdate(
                file=file,
                token=token,
                filename=filename,
                replace_if_exist=replace_if_exist,
            )

    return FixedContentQueryChecker(content_type, file_max_size)
