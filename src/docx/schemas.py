from datetime import datetime
from typing import Annotated, Sequence, Dict, Union, Any, Iterable
from pathlib import Path

import jwt
from jwt import InvalidAudienceError, ExpiredSignatureError, DecodeError
from logrich.logger_ import log  # noqa
from pathvalidate import sanitize_filepath
from pydantic import BaseModel, Field, EmailStr, SecretStr

from src.docx.config import config

from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal

from src.docx.helpers.tools import get_key

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

    issuer: Any = None


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

    filename: str
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
        key = await get_key(f"authorized_keys/{self.issuer.lower()}.pub")
        return key

    def set_issuer(self) -> None:
        """Извлекает издателя токена"""
        # установим издателя токена, для этого прочитаем нагрузку без валидации.
        claimset_without_validation = jwt.decode(
            jwt=self.token, options={"verify_signature": False}
        )
        sanitize_issuer = str(sanitize_filepath(claimset_without_validation.get("iss", "")))
        self.issuer = sanitize_issuer.strip().replace(".", "_").replace("-", "_")

    @property
    async def decode_jwt(self) -> DataModel:
        try:
            # определяем наличие разрешения
            # валидируем токен
            decoded_payload = jwt.decode(
                jwt=self.token,
                audience=self.audience,
                key=await self.pub_key,
                algorithms=[self.algorithm],
            )
            resp = DataModel(**decoded_payload)
            # добавим в вывод имя папки данного издателя токена
            resp.issuer = self.issuer
            return resp
        except InvalidAudienceError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_AUD_NOT_FOUND.value)
        except ExpiredSignatureError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_EXPIRE.value)
        except ValueError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.INVALID_TOKEN.value)
        except DecodeError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT.value)
