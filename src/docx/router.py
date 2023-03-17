from pathlib import Path
import shutil
from fastapi import FastAPI, Depends, Form, UploadFile
from logrich.logger_ import log  # noqa
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter, check_file_exist
from src.docx.config import config
from src.docx.depends import (
    Audience,
    JWTBearer,
    file_checker_wrapper,
)
from src.docx.exceptions import ErrorModel, ErrorCodeLocal

from src.docx.helpers.tools import dict_hash
from src.docx.schemas import (
    JWT,
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


@router.put(
    "/template-upload",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.UPDATE.value}**",
    response_model=DocxUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_template(
    payload: DataModel = Depends(JWTBearer(audience=Audience.UPDATE.value), use_cache=True),
    file: UploadFile = Depends(file_checker_wrapper()),
    filename: str = Form(
        "",
        description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
        "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
    ),
    replace_if_exist: bool = Form(
        False, description=f"Заменить шаблон, если он существует. {bool_description}"
    ),
) -> DocxUpdateResponse:
    file_name = file.filename
    if filename:
        file_name = filename
    saved_name = Path(f"{config.TEMPLATES_DIR}/{payload.issuer}/{file_name}")
    resp = DocxUpdateResponse()
    # проверим существование
    await check_file_exist(name=saved_name, replace_if_exist=replace_if_exist)
    # создадим вложенную папку
    if not Path(saved_name).parent.is_dir():
        Path(saved_name).parent.mkdir()
    with open(saved_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    if Path(saved_name).is_file():
        resp.template = saved_name
    return resp


@router.post(
    "/create",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.CREATE.value}**",
    response_model=DocxResponse,
    # dependencies=[ Depends(JWTBearer(audience=Audience.CREATE.value), use_cache=True)],
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
    # payload: DocxCreate = Depends(),
    token: DataModel = Depends(JWTBearer(audience=Audience.CREATE.value), use_cache=True),
) -> DocxResponse:
    """Создать файл *.docx по шаблону"""
    await check_file_exist(payload.template, replace_if_exist=False)
    # token = JWT(token=payload.token)
    log.debug(payload)
    log.debug(token.issuer)
    # return DocxUpdateResponse()
    doc = DocxTemplate(Path(f"{config.TEMPLATES_DIR}/{token.issuer}/{payload.template}"))
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
