from pathlib import Path
import shutil
from typing import Any

import magic
from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException, Header, Body
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter, check_file_exist
from src.docx.config import config
from src.docx.depends import (
    Audience,
    # file_checker_wrapper,
    JWTBearer,
    # FixedContentQueryChecker,
    file_checker_wrapper,
)
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.helpers.security import JWT
from src.docx.helpers.tools import dict_hash
from src.docx.schemas import (
    DocxCreate,
    DocxResponse,
    DocxUpdateResponse,
    DataModel,
    bool_description,
)

router = APIRouter()


@router.get(
    "/templates",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.READ.value}**",
    response_model=list,
    status_code=status.HTTP_200_OK,
)
def list_templates(payload: DataModel = Depends(JWTBearer(audience=Audience.READ.value))) -> list:
    # log.debug(payload)
    p = Path(f"templates/{payload.issuer}").glob("**/*.docx")
    files = [x for x in p if x.is_file()]
    return files


# checker = file_checker_wrapper(
#     content_type=config.content_type_white_list, file_max_size=config.FILE_MAX_SIZE
# )


@router.put(
    "/template-upload",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.UPDATE.value}**",
    response_model=DocxUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_template(
    # data: DocxUpdateTplFile=Depends(),
    payload: DataModel = Depends(JWTBearer(audience=Audience.UPDATE.value), use_cache=True),
    file: UploadFile = Depends(file_checker_wrapper()),
    # data=Depends(file_checker_wrapper()),
    # data: str = Form(...),
    # filename: str = Body(...),
    filename: str = Form(
        None,
        description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
        "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
    ),
    replace_if_exist: bool = Form(
        False, description=f"Заменить шаблон, если он существует. {bool_description}"
    ),
    # ) -> dict:
) -> DocxUpdateResponse:
    # return {}
    log.debug(payload)
    # token_ = JWT(token=payload.token)
    # log.info("", o=token_.issuer)
    # log.debug(data)
    # return DocxUpdateResponse()
    log.debug(filename)
    log.debug(replace_if_exist)
    file_name = filename

    if filename:
        file_name = filename
    log.debug(file)
    log.debug(file_name)
    saved_name = f"{config.TEMPLATES_DIR}/{payload.issuer}/{file_name}"
    resp = DocxUpdateResponse()
    # log.debug(Path(saved_name).parent)
    # проверим существование
    await check_file_exist(name=saved_name, replace_if_exist=replace_if_exist)
    # создадим вложенную папку
    if not Path(saved_name).parent.is_dir():
        Path(saved_name).parent.mkdir()
    with open(saved_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    if Path(saved_name).is_file():
        #     log.debug(saved_name)
        resp.template = saved_name
    return resp


@router.post(
    "/create",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.CREATE.value}**",
    # dependencies=[Depends(check_create_access)],
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

    token = JWT(token=payload.token)
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
