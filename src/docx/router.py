import inspect
import json
import pathlib
import shutil
from json import JSONDecodeError
from typing import List, Optional, Annotated, Generator, Callable, Any, Dict, Type

from fastapi import FastAPI, Depends, UploadFile, Form, HTTPException, Body, Header
from fastapi.encoders import jsonable_encoder
from fastapi.params import File
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, ValidationError, Field, validator, PositiveInt
from pydantic.fields import ModelField
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.depends import check_create_access, Audience, check_update_access
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.helpers.security import Jwt, decode_jwt
from src.docx.helpers.tools import dict_hash
from src.docx.schemas import DocxCreate, DocxResponse, DocxUpdate

router = APIRouter()


class Base(BaseModel):
    token: str
    filename: str
    point: Optional[float] = None
    is_accepted: Optional[bool] = False

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            log.trace(value)
            # return value
            return cls(**json.loads(value))
        return value


models = {
    "base": Base,
}


class DataChecker:
    # https://stackoverflow.com/questions/65504438/how-to-add-both-file-and-json-body-in-a-fastapi-post-request
    def __init__(self, name: str):
        self.name = name

    def __call__(self, data: str = Form(...)):
        try:
            log.debug(self.name)
            # model = models[self.name].json(data)
            # model = models[self.name].dict(data)
            # model = models[self.name].parse_obj(data)
            model = Base.parse_raw(data)
            # model = models[self.name].parse_raw(data)
            log.trace(model)
        except ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return model


base_checker: Base = DataChecker("base")
# other_checker = DataChecker("other")


class Base2(BaseModel):
    # token: str
    # filename: str | None = None
    # filename: str = Form(
    #     None,
    #     description="Сериализованный список имён файлов, файлы будут сохранены под указанными именами. Если имена не указаны файлы сохранятся как есть.",
    # ),
    # token: str = Form(...),
    # files:Annotated[list[UploadFile], File(None, description="A file read as UploadFile")]
    # file: UploadFile
    file: Annotated[str, Field(min_length=10, max_length=100)]

    # file:UploadFile = File(description="A file read as UploadFile",
    #                        title='some title'
    #                        # min_length=10
    #                        )
    # file: Annotated[UploadFile, File(description="A file read as UploadFile", gt=0)]
    # @validator("filename")
    # def decode_filenames(cls, val: str, values: dict) -> str:
    #     try:
    #         if val:
    #             log.debug(values)
    #             return json.loads(val)
    #     except JSONDecodeError as e:
    #     #     log.trace(e)
    #         raise HTTPException(
    #             detail=f'Поле filename невозможно сериализовать: {val}',
    #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         )

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     # self(**json.loads())
    #     filename = kwargs.get("filename", "")
    #     if filename:
    #         self.filename = json.loads(filename)
    #     log.debug(kwargs)
    # self.name = name

    # @classmethod
    # def __get_validators__(cls):
    #     yield cls.validate_to_json
    #
    # @classmethod
    # def validate_to_json(cls, value):
    #     if isinstance(value, str):
    #         log.trace(value)
    #         return value
    #         # return cls(**json.loads(value))
    #     return value

    # def __call__(self, data: str = Form(...)):
    #     try:
    #         log.debug(self.name)
    #         # model = models[self.name].json(data)
    #         # model = models[self.name].dict(data)
    #         # model = models[self.name].parse_obj(data)
    #         model = Base.parse_raw(data)
    #         # model = models[self.name].parse_raw(data)
    #         log.trace(model)
    #     except ValidationError as e:
    #         raise HTTPException(
    #             detail=jsonable_encoder(e.errors()),
    #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         )
    #     return model


async def valid_content_length(content_length: int = Header(..., lt=80_000)):
    return content_length

    # @classmethod
    # def __modify_schema__(cls, field_schema: Dict[UploadFile, Any], field: Optional[ModelField]):
    #     if field:
    # size = field.field_info.extra['size']
    # field_schema["examples"] = "lijjuojh"

    # f: UploadFile = File(..., description="description", media_type="multipart/form-data")


async def get_file(
    file: UploadFile
    | None = File(
        ...,
        description=f"Максимальный размер загружаемого файла: **{config.FILE_MAX_SIZE}** Mb",
    )
) -> UploadFile:
    # log.debug(file.size)
    if file.size > config.FILE_MAX_SIZE * 1024 * 1024:
        raise HTTPException(
            detail="Файл слишком большой, {:.2f} Mb".format(file.size / 1024 / 1024),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return file


@router.post(
    "/template-upload",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.UPDATE.value}**",
    dependencies=[Depends(check_update_access)],
    response_model=set[str],
    status_code=status.HTTP_200_OK,
)
async def upload_template(
    file: get_file = Depends(),
    filename: str = Form(
        None,
        description="Файл будет сохранен под указанным именем. Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
    ),
    # token: DocxUpdate = Form(...)
    #     ...,
    # description="Файл будет сохранен под указанным именем. Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
    # ),
) -> set:
    # log.info(token)
    log.debug(filename)
    log.trace(file.filename)

    resp = set()
    return resp
    for file in data.files:
        log.debug(file.filename)
        # log.trace(dir(file))
        saved_name = f"{config.DOWNLOADS_DIR}/{file.filename}"
        with open(saved_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            resp.add(saved_name)
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
    pathlib.Path(path_to_save).mkdir(parents=True, exist_ok=True)
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
