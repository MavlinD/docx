import inspect
import json
import pathlib
import shutil
from json import JSONDecodeError
from typing import List, Optional, Annotated, Generator, Callable, Any, Dict, Type

from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, Body, Header
from fastapi.encoders import jsonable_encoder
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, ValidationError, Field, validator, PositiveInt
from pydantic.fields import ModelField
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.depends import check_create_access, Audience
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.helpers.security import Jwt
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


class GroupRename(BaseModel):
    """схема параметров запроса на переименование группы"""

    group: str = Field(
        min_length=10,
        max_length=100,
        description="имя/ID/slag группы для изменения",
    )
    # file = Body(description="A file read as UploadFile", title='some title')
    # file = Body(description="A file read as UploadFile", title='some title', gt=10)
    # file = File(description="A file read as UploadFile", title='some title', max_length=10_00)
    # file: UploadFile = File(description="A file read as UploadFile", title='some title', max_length=10_00)
    # file: Annotated[UploadFile, File(description="A file read as UploadFile")]
    # file: Annotated[UploadFile, File(description="A file read as UploadFile", gt=0)]


# try:
#     # this won't work since PositiveInt takes precedence over the
#     # constraints defined in Field meaning they're ignored
#     class Model(BaseModel):
#         foo: PositiveInt = Field(..., lt=10)
# except ValueError as e:
#     print(e)
#     """
#     On field "foo" the following field constraints are set but not enforced:
#     lt.
#     For more details see https://docs.pydantic.dev/usage/schema/#unenforced-
#     field-constraints
#     """


class Model(BaseModel):
    # file: UploadFile = Body(..., exclusiveMaximum2=10)
    file: UploadFile
    # = File(..., description='description222')
    # @validator("file")
    # def decode_filenames(cls, val: UploadFile, values: dict) -> UploadFile:
    #     try:
    #         if val.size>1:
    #             log.debug(val)
    #             return val
    # #             # return json.loads(val)
    #     except Exception as e:
    #         log.trace(e)
    #         # raise HTTPException(
    #         #     detail=f'Поле filename невозможно сериализовать: {val}',
    #         #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         # )
    # @classmethod
    # def __modify_schema__(
    #     cls, field_schema: Dict[str, Any], field: Optional[ModelField]
    # ):
    #     field_schema['description'] = 'kjhkhkjh'
    # if field:
    #     size = field.field_info.extra['size']
    #     field_schema['examples'] = [c * 3 for c in size]


class RestrictedAlphabetStr(UploadFile):
    # class RestrictedAlphabetStr(str):

    value: UploadFile = File(...)

    # @classmethod
    # def __get_validators__(cls) -> Generator[Callable, None, None]:
    #     yield cls.validate
    #
    # @classmethod
    # def validate(cls, value: UploadFile, field: UploadFile):
    #     size = field.field_info.extra['size']
    #     log.debug(field)
    #     log.debug(value)
    #     log.debug(size)
    #     if any(c not in size for c in value):
    #         raise ValueError(f'{value!r} is not restricted to {size!r}')
    #     return cls(value)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[UploadFile, Any], field: Optional[ModelField]):
        if field:
            # size = field.field_info.extra['size']
            field_schema["examples"] = "lijjuojh"


class SimpleModel(BaseModel):
    no: int = Body(...)
    # nm: str = Form(...)
    f: UploadFile = Body(..., example="kjhkjh")

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[UploadFile, Any], field: Optional[ModelField]):
        if field:
            # size = field.field_info.extra['size']
            field_schema["examples"] = "lijjuojh"


def as_form(cls: Type[BaseModel]) -> Type[BaseModel]:
    """
    Adds an `as_form` class method to decorated models. The `as_form` class
    method can be used with `FastAPI` endpoints.

    Args:
        cls: The model class to decorate.

    Returns:
        The decorated class.

    """

    def make_form_parameter(field: ModelField) -> Any:
        """
        Converts a field from a `Pydantic` model to the appropriate `FastAPI`
        parameter type.

        Args:
            field: The field to convert.

        Returns:
            Either the result of `Form`, if the field is not a sub-model, or
            the result of `Depends` if it is.

        """
        if issubclass(field.type_, BaseModel):
            # This is a sub-model.
            assert hasattr(field.type_, "as_form"), (
                f"Sub-model class for {field.name} field must be decorated with" f" `as_form` too."
            )
            return Depends(field.type_.as_form)
        else:
            return Form(field.default) if not field.required else Form(...)

    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=make_form_parameter(field),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
class Nested(BaseModel):
    foo: int
    bar: str


@as_form
class Outer(BaseModel):
    inner: UploadFile = File(...)
    baz: float


# class MyModel:
class MyModel(BaseModel):
    # value: RestrictedAlphabetStr = File(size='100', media_type= "multipart/form-data")
    # f: Annotated[
    #         UploadFile,
    #         File
    # ]
    #         File(...,description='description')
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.field_schema["description"] = "lijjuojh"

    f: UploadFile = File(..., description="description", media_type="multipart/form-data")

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any], field: Optional[ModelField]):
        # if field:
        # size = field.field_info.extra['size']
        cls.field_schema["description"] = "lijjuojh"

    # class Config:
    #     title = 'Main'
    # file: Any = File(...)
    # file: int = Body(..., gt=10000)


def valf(content_length):
    # async def valf(content_length: int = Header(..., lt=80_000)):
    #     return  File(None,description='description')
    return Annotated[UploadFile, File(None, description="description")]


# async def wrap(q, arg):
async def common_parameters(q: UploadFile | None = File(..., description=f"jhgjhg")):
    # return {"q": File(..., description='description') }
    return {
        "q": q,
    }
    # r = await common_parameters(q=q)
    # return r


class FixedContentQueryChecker:
    def __init__(self, limit: int = 4):
        self.limit = limit
        self.f = File(..., description=f"jhgjhglimit")
        # log.trace(self.f)

    def __call__(
        self, q: UploadFile | None = File(..., description=f"jhgjhglimit{config.LOG_LEVEL}")
    ):
        # log.debug(self.f)
        # if q<10:
        #     return self.limit
        return {
            "q": q,
        }


checker = FixedContentQueryChecker(limit=10)


@router.post(
    "/template-upload",
    summary=" ",
    description=f"Требуется аудиенция: **{Audience.UPDATE.value}**",
    # dependencies=[Depends(check_create_access)],
    response_model=set[str],
    openapi_extra={"limit": 10},
    status_code=status.HTTP_200_OK,
)
async def upload_template(
    # file: BaseModel
    # file: MyModel=Depends()
    # file: Model=Depends()
    fixed_content_included: dict = Depends(checker),
    # commons: dict = Depends(common_parameters)
    # commons: UploadFile = Depends(File)
    # file: Model
    #     form: Outer = Depends(Outer.as_form)
    #     form_data: SimpleModel = Depends()
    # file: bytes = File(description='jhgjgg', examples='jhgjg')
    # foo: UploadFile = File(...,description='description'),
    # file: Depends(MyModel)
    # value: MyModel
    # name: str,
    # model: Base = Depends(base_checker),
    # data: Base = Body(...),
    # data: Base = Depends(Base),
    #     payload: GroupRename,
    # data: Base2 ,
    # data: Base2 = Depends(),
    #     filename: str = Form(...),
    #     token: str = Form(...),
    # data: Base = Depends(base_checker),
    # foo:RestrictedAlphabetStr,
    # foo:MyModel,
    # foo: UploadFile =MyModel,
    # baz: str = Body(...),
    # file: Model,
    # filename: str = Form(
    #     None,
    #     description="Сериализованный список имён файлов, файлы будут сохранены под указанными именами. Если имена не указаны файлы сохранятся как есть.",
    # ),
    #     file: Annotated[
    #         str, Field(min_length=10, max_length=100)
    #     ]
    # token: str = Form(...),
    # file: UploadFile = Depends(MyModel),
    # file: UploadFile = File(...),
    #     file = File(..., gt=10_0),
    #     foo: PositiveInt = Field(..., exclusiveMaximum=10)
    #     file_size: int = Depends(valid_content_length)
    # file: UploadFile = File(description="A file read as UploadFile", title='some title',
    # gt=10
    # ),
) -> set:
    # log.trace(payload.name)
    # log.trace(file)
    # log.trace(foo)
    # log.trace(data)
    # log.trace(name)
    # log.debug(token)
    # log.trace(filename)
    # contents = await file.read()
    # log.trace(contents)
    # await file.write(contents)
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
