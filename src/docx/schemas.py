from datetime import datetime
from typing import Annotated, Sequence, Dict, Union, Any, Iterable
from pathlib import Path

import jwt
from logrich.logger_ import log  # noqa
from pathvalidate import sanitize_filepath
from pydantic import BaseModel, Field, EmailStr, SecretStr, validator

from src.docx.config import config

from src.docx.exceptions import (
    InvalidVerifyToken,
    ErrorCodeLocal,
    NameSpaceNotSet,
    IssuerNotSet,
    IssuerPubKeyNotFound,
)

from src.docx.helpers.tools import get_key, jwt_exception

token_description = (
    f"**JWT** подписанный асинхронным алгоритмом из списка {config.ALGORITHMS_WHITE_LIST},"
    f"<br>**Аудиенция токена** должна соотвествовать аудиенции конечной точки."
    f"<br>Издатель должен её включить в токен перед запросом."
)

bool_description = f"<br>Соглашение о преобразовании типов: **True, true, 1, yes, on** будут преобразованы к Истине."


def file_description(content_type: dict | None = None, file_max_size: float | None = None) -> str:
    """Описание ограничения для поля file. Используется в OpenAPI."""
    resp: list = []
    if content_type:
        resp.append(f"Разрешены следующие типы файлов: __{', '.join(content_type.keys())}__")
    if file_max_size:
        resp.append(f"Максимальный размер загружаемого файла: **{file_max_size}** Mb")
    return "<br>".join(resp)


SecretType = Union[str, SecretStr]


class DataModel(BaseModel):
    """Common model, for params, responses & other case."""

    class Config:
        extra = "allow"

    issuer: str = ""
    nsp: str = ""

    @validator("nsp")
    def check_nsp(cls, v: str) -> str:
        """rise if nsp not exist"""
        if not v:
            raise NameSpaceNotSet(f"Поле токена nsp: {v}")
        if v.find(",") != -1:
            # это когда пользователь входит в несколько групп вида nsp_*
            raise NameSpaceNotSet(f"Поле токена nsp не должно содержать запятых: {v}")
        return v

    @validator("issuer")
    def check_issuer(cls, v: str) -> str:
        """rise if issuer not exist"""
        if not v:
            raise IssuerNotSet(f"Поле токена iss: {v}")
        return v


def get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


class DocxCreate(BaseModel):
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

    template: Path = Field(
        description="Имя заранее загруженного шаблона",
    )


class DocxResponse(BaseModel):
    """схема для ответа на создание отчета"""

    filename: str | Path
    url: str


class DocxUpdateResponse(BaseModel):
    """схема для ответа на изменение отчета"""

    template: Path | None = None


class DocxTemplatesListResponse(BaseModel):
    """схема для ответа на запрос списка шаблонов"""

    templates: list = []


class TokenCustomModel(BaseModel):
    """
    Модель пользовательского токена, для валидации параметров запроса пользовательского токена
    только для тестов.
    """

    iss: str = Field(description="издатель токена")
    sub: str | None = Field(default=None, description="тема токена")
    type: str = Field(default="access", description="тип токена")
    nsp: str | None = Field(default="", description="namespace или папка пользователя")
    exp: datetime
    email: EmailStr | None = None
    aud: Sequence[str] = Field(
        description="Аудиенция, издатель должен её определить и включить в токен перед запросом."
    )


class JWT:
    """base operation with jwt"""

    def __init__(self, token: str = "") -> None:
        # log.warning(token)
        self.token = token
        self.issuer = ""
        self._pub_key = ""
        self._algorithm = ""
        self._audience: str | Iterable[str] | None = None

    @property
    def audience(self) -> str | Iterable[str] | None:
        return self._audience

    @audience.setter
    def audience(self, value: str | Iterable[str] | None) -> None:
        self._audience = value

    @property
    def algorithm(self) -> str:
        """Получить алгоритм подписи токена, без валидации."""
        header = jwt.get_unverified_header(self.token)
        algorithm = header.get("alg", "")
        if algorithm not in config.ALGORITHMS_WHITE_LIST:
            log.err("алгоритм подписи токена странен(", o=header)
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_ALGORITHM_NOT_FOUND.value)
        return algorithm

    @property
    async def pub_key(self) -> str:
        # log.trace("read pub key")
        try:
            key = await get_key(f"authorized_keys/{self.issuer}.pub")
            return key
        except FileNotFoundError:
            raise IssuerPubKeyNotFound(msg=self.issuer)

    @jwt_exception
    def set_issuer(self) -> None:
        """Извлекает издателя токена"""
        # установим издателя токена, для этого прочитаем нагрузку без валидации.
        claimset_without_validation = jwt.decode(
            jwt=self.token, options={"verify_signature": False}
        )
        # log.debug(claimset_without_validation)
        sanitize_issuer = str(sanitize_filepath(claimset_without_validation.get("iss", "")))
        issuer = sanitize_issuer.strip().replace(".", "_").replace("-", "_").lower()
        if not issuer:
            raise IssuerNotSet
        self.issuer = issuer

    @property
    @jwt_exception
    async def decode_jwt(self) -> DataModel:
        # log.trace(self.audience)
        decoded_payload = jwt.decode(
            jwt=self.token,
            audience=self.audience,
            key=await self.pub_key,
            algorithms=[self.algorithm],
        )

        decoded_payload.setdefault("nsp", "")
        decoded_payload.setdefault("iss", "")
        # log.debug("", o=decoded_payload)
        resp = DataModel(**decoded_payload)
        # добавим в вывод имя папки данного издателя токена
        resp.issuer = self.issuer
        return resp
