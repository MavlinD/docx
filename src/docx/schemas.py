from datetime import datetime
from typing import Annotated, Sequence, Dict
from pathlib import Path

import jwt
from fastapi import UploadFile, File, Form, Body, Depends
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field, validator, EmailStr

from src.docx.config import config

from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal
from src.docx.helpers.tools import get_key

token_description = (
    f"**JWT** подписанный асинхронным алгоритмом из списка {config.ALGORITHMS_WHITE_LIST},"
    f"<br>**Аудиенция токена** должна соотвествовать аудиенции конечной точки."
    f"<br>Издатель должен её включить в токен перед запросом."
)

bool_description = f"<br>Соглашение о преобразовании типов: **True, true, 1, yes, on** будут преобразованиы к Истине."


def file_description(content_type: dict | None = None, file_max_size: int | None = None) -> str:
    resp: list = []
    if content_type:
        # description=f"Разрешены следующие типы файлов: __{', '.join(config.content_type_white_list.keys())}__<br>"
        resp.append(f"Разрешены следующие типы файлов: __{', '.join(content_type.keys())}__")
    if file_max_size:
        resp.append(f"Максимальный размер загружаемого файла: **{file_max_size}** Mb")
        # file_max_size = config.FILE_MAX_SIZE
    # log.debug(resp)
    return "<br>".join(resp)
    # return f"Разрешены следующие типы файлов: __{content_type}__<br>Максимальный размер загружаемого файла: **{file_max_size}** Mb"


class Token(BaseModel):
    """Схема для обновления/загрузки отчета"""

    token: str


class DocxUpdate(BaseModel):
    """Схема для обновления/загрузки отчета"""

    token: str
    file: UploadFile
    filename: str
    replace_if_exist: bool


# def file_upload_payload():
#     return {
#         "file": UploadFile,
#         # file: UploadFile = Depends(check_file_size),
#         "filename": Form(
#             None,
#             description="Шаблон будет сохранен под указанным именем. Папки будут созданы при необходимости.<br>"
#             "Если имя не указано, то файл сохранится как есть, с учетом замены определенных символов.",
#         ),
#         "token": Form(...),
#         "replace_if_exist": Form(
#             False, description=f"Заменить шаблон, если он существует. {bool_description}"
#         ),
#     }


class JWToken(BaseModel):
    token: str = Body(
        description=token_description,
    )


class DocxCreate(JWToken):
    """Схема для создания отчета"""

    filename: Annotated[
        str,
        Field(
            min_length=config.FILENAME_MIN_LENGTH,
            max_length=config.FILENAME_MAX_LENGTH,
            description="Имя создаваемого файла",
        ),
    ]

    context: Dict[str, str] = Field(default={}, description="Переменные шаблона")

    template: Annotated[
        str,
        Field(
            min_length=config.TEMPLATE_MIN_LENGTH,
            max_length=config.TEMPLATE_MAX_LENGTH,
            description="Имя заранее загруженного шаблона",
        ),
    ]

    @validator("template")
    def template_must_be_exist(cls, v: str, values: dict) -> Path:
        """make Path from string"""
        token = Jwt(token=values.get("token", ""))
        tpl_place = Path(f"{config.TEMPLATES_DIR}/{token.issuer}/{v}")
        if not tpl_place.is_file():
            raise ValueError(f"Template {tpl_place} not exist!")
        return tpl_place


class DocxResponse(BaseModel):
    """схема для ответа на создание отчета"""

    filename: str
    url: str


class DocxUpdateResponse(BaseModel):
    """схема для ответа на изменение отчета"""

    template: str | None = None


class TokenCustomModel(BaseModel):
    """
    Модель пользовательского токена, для валидации параметров запроса пользовательского токена
    только для тестов.
    """

    iss: str = Field(description="издатель токена")
    sub: str | None = Field(default=None, description="тема токена")
    type: str = Field(default="access", description="тип токена")
    exp: datetime
    email: EmailStr | None = None
    aud: Sequence[str] = Field(
        description="Аудиенция, издатель должен её определить и включить в токен перед запросом."
    )


class Jwt:
    """base operation with jwt"""

    def __init__(self, token: str) -> None:
        self.token = token
        self._issuer = ""
        self._pub_key = ""
        self._algorithm = ""

    @property
    def algorithm(self) -> str:
        header = jwt.get_unverified_header(self.token)
        algorithm = header.get("alg", "")
        if algorithm not in config.ALGORITHMS_WHITE_LIST:
            log.err("алгоритм подписи токена странен(", o=header)
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_ALGORITHM_NOT_FOUND.value)
        return algorithm

    @property
    async def pub_key(self) -> str:
        # log.trace("read pub key")
        key = await get_key(f"public_keys/{self.issuer.lower()}.pub")
        return key

    @property
    def issuer(self) -> str:
        """извлекает издателя токена"""
        # установим издателя токена, для этого прочитаем нагрузку без валидации.
        claimset_without_validation = jwt.decode(
            jwt=self.token, options={"verify_signature": False}
        )
        return (
            claimset_without_validation.get("iss", "").strip().replace(".", "_").replace("-", "_")
        )
