from pathlib import Path
import shutil
from fastapi import FastAPI, Depends, Form, UploadFile
from logrich.logger_ import log  # noqa
from starlette import status
from docxtpl import DocxTemplate
from fastapi.responses import FileResponse

from src.docx.assets import APIRouter, check_file_exist
from src.docx.config import config
from src.docx.depends import (
    JWTBearer,
    file_checker_wrapper,
    JWT_STATUS_HTTP_403_FORBIDDEN,
    FILE_STATUS_HTTP_404_NOT_FOUND,
    AudienceCompose,
)
from src.docx.exceptions import ErrorModel, ErrorCodeLocal, FileNotExist

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
    "/download/{filename:path}",
    summary=" ",
    description=f"Требуется одна из аудиенций: **{AudienceCompose.READ}**",
    responses={
        status.HTTP_403_FORBIDDEN: JWT_STATUS_HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND: FILE_STATUS_HTTP_404_NOT_FOUND,
    },
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def download_template(
    filename: str,
    payload: DataModel = Depends(JWTBearer(audience=AudienceCompose.READ)),
) -> FileResponse:
    # log.debug(filename)
    path = Path(f"templates/{payload.issuer}/{filename}")
    if not path.is_file():
        raise FileNotExist(msg=ErrorCodeLocal.TEMPLATE_NOT_EXIST.value)
    ret = FileResponse(
        path=path,
        filename=filename,
        media_type="multipart/form-data",
    )
    return ret


@router.get(
    "/templates",
    summary=" ",
    description=f"Требуется одна из аудиенций: **{AudienceCompose.READ}**",
    responses={
        status.HTTP_403_FORBIDDEN: JWT_STATUS_HTTP_403_FORBIDDEN,
    },
    response_model=list,
    status_code=status.HTTP_200_OK,
)
async def list_templates(
    payload: DataModel = Depends(JWTBearer(audience=AudienceCompose.READ)),
) -> list:
    """список шаблонов на сервисе"""
    # log.debug(payload)
    p = Path(f"templates/{payload.issuer}").glob("**/*.docx")
    files = [x for x in p if x.is_file()]
    return files


@router.put(
    "/template-upload",
    summary=" ",
    description=f"Требуется одна из аудиенций: **{AudienceCompose.UPDATE}**",
    response_model=DocxUpdateResponse,
    responses={
        status.HTTP_403_FORBIDDEN: JWT_STATUS_HTTP_403_FORBIDDEN,
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.FILE_IS_TOO_LARGE: {
                            "summary": "Размер файла превышает допустимый.",
                            "value": {"detail": ErrorCodeLocal.FILE_IS_TOO_LARGE},
                        },
                        ErrorCodeLocal.FILE_EXTENSION_REJECT: {
                            "summary": "Данный тип файла не разрешен.",
                            "value": {"detail": ErrorCodeLocal.FILE_EXTENSION_REJECT},
                        },
                    }
                }
            },
        },
    },
    status_code=status.HTTP_201_CREATED,
)
async def upload_template(
    payload: DataModel = Depends(JWTBearer(audience=AudienceCompose.UPDATE)),
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
    # log.warning(config.FILE_MAX_SIZE)
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
    description=f"Требуется одна из аудиенций: **{AudienceCompose.CREATE}**",
    response_model=DocxResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: JWT_STATUS_HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND: FILE_STATUS_HTTP_404_NOT_FOUND,
    },
)
async def create_docx(
    payload: DocxCreate,
    token: DataModel = Depends(JWTBearer(audience=AudienceCompose.CREATE), use_cache=True),
) -> DocxResponse:
    """Создать файл *.docx по шаблону"""
    await check_file_exist(payload.template, replace_if_exist=False)
    doc = DocxTemplate(Path(f"{config.TEMPLATES_DIR}/{token.issuer}/{payload.template}"))
    doc.render(payload.context)
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
