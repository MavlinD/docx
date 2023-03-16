from pathlib import Path
import shutil

import magic
from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter, check_file_exist
from src.docx.config import config
from src.docx.depends import (
    check_create_access,
    Audience,
    check_update_access,
    check_file_size,
    check_content_type,
    check_file_condition,
)
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.helpers.security import Jwt
from src.docx.helpers.tools import dict_hash
from src.docx.schemas import (
    DocxCreate,
    DocxResponse,
    DocxUpdateResponse,
    bool_description,
    token_description,
    file_description,
    Token,
    DocxUpdate,
)

router = APIRouter()


class FileUploadPayload:
    # class FileUploadPayload(BaseModel):
    def __init__(
        self,
        # file:UploadFile=File(),
        # file:File,
        file: UploadFile = Depends(check_file_size),
        token: str = Form(..., description=f"dsrfgvdf"),
        filename: str = Form(
            None,
            description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
            "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
        ),
        replace_if_exist: bool = Form(
            False, description=f"Заменить шаблон, если он существует. {bool_description}"
        ),
    ):
        self.file = file
        self.filename = filename
        self.token = token
        self.replace_if_exist = replace_if_exist

    def __call__(self, *args, **kwargs):
        ...


# LIMIT='bar'

# LIMIT='foo'


def ff(content_type: dict, file_max_size: int):
    class FixedContentQueryChecker:
        # https://stackoverflow.com/questions/65504438/how-to-add-both-file-and-json-body-in-a-fastapi-post-request

        def __init__(self, content_type: dict, file_max_size: int):
            self.content_type = content_type
            self.file_max_size = file_max_size

        def __call__(
            self,
            # file: UploadFile = Form(..., description=arg),
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
        ):
            # if file:
            #     return self.fixed_content in file
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

            return {
                "file": file,
                "token": token,
                "filename": filename,
                "replace_if_exist": replace_if_exist,
            }

    checker = FixedContentQueryChecker(content_type, file_max_size)
    return checker
    # return Form(..., description=arg)


checker = ff(content_type=config.content_type_white_list, file_max_size=config.FILE_MAX_SIZE)


@router.post(
    "/template-upload",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.UPDATE.value}**",
    dependencies=[
        Depends(check_update_access, use_cache=True),
        # Depends(check_file_condition, use_cache=True),
        # Depends(check_content_type),
        # Depends(check_file_size),
    ],
    response_model=DocxUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_template(
    payload: dict = Depends(checker),
    # file: UploadFile = Depends(check_file_size),
    # file: UploadFile,
    # filename: str = Form(
    #     None,
    #     description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
    #     "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
    # ),
    # token: str = Form(...),
    # replace_if_exist: bool = Form(
    #     False, description=f"Заменить шаблон, если он существует. {bool_description}"
    # ),
    # payload: FileUploadPayload = Depends(),
    # ) -> dict:
) -> DocxUpdateResponse:
    log.debug(payload)
    payload2 = DocxUpdate(**payload)
    # return {"payload": payload}
    # return
    token_ = Jwt(token=payload2.token)
    log.warning(token_.token)
    file_name = payload2.file.filename
    log.trace(file_name)
    if payload2.filename:
        file_name = payload2.filename
    saved_name = f"{config.TEMPLATES_DIR}/{token_.issuer}/{file_name}"
    resp = DocxUpdateResponse()
    # log.debug(Path(saved_name).parent)
    # проверим существование
    await check_file_exist(name=saved_name, replace_if_exist=payload2.replace_if_exist)
    # создадим вложенную папку
    if not Path(saved_name).parent.is_dir():
        Path(saved_name).parent.mkdir()
    with open(saved_name, "wb") as buffer:
        shutil.copyfileobj(payload2.file.file, buffer)
    if Path(saved_name).is_file():
        #     log.debug(saved_name)
        resp.template = saved_name
    return resp


@router.post(
    "/create",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.CREATE.value}**",
    dependencies=[Depends(check_create_access)],
    response_model=DocxResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
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
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.TEMPLATE_NOT_EXIST: {
                            "summary": "Указанный шаблон не найден.",
                            "value": {"detail": ErrorCodeLocal.TEMPLATE_NOT_EXIST},
                        },
                    }
                }
            },
        },
    },
)
async def create_docx(
    payload: DocxCreate,
) -> DocxResponse:
    """Создать файл *.docx по шаблону"""

    token = Jwt(token=payload.token)
    doc = DocxTemplate(payload.template)
    doc.render(payload.context)
    # log.debug(dir(dependencies))
    # log.debug(dependencies)
    # формируем уникальную ссылку на файл
    hash_payload = dict_hash(payload.context)[-8:]
    path_to_save = f"{config.DOWNLOADS_DIR}/{token.issuer}"
    Path(path_to_save).mkdir(parents=True, exist_ok=True)
    filename = f"{path_to_save}/{payload.filename}-{hash_payload}.docx"
    doc.save(filename=filename)

    resp = DocxResponse(
        filename=filename,
        url=f"{config.DOWNLOADS_URL}/{token.issuer}/{payload.filename}-{hash_payload}.docx",
    )
    return resp


prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(router, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
