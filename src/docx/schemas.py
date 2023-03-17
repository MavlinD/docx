from datetime import datetime, timedelta
from functools import lru_cache
from typing import Annotated, Sequence, Dict, Union
from pathlib import Path

import jwt
from fastapi import UploadFile, File, Form, Body, Depends
from jwt import InvalidAudienceError, ExpiredSignatureError, DecodeError
from logrich.logger_ import log  # noqa
from pathvalidate import sanitize_filepath
from pydantic import BaseModel, Field, validator, EmailStr, SecretStr

from src.docx.config import config

from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal

# from src.docx.helpers.security import SecretType, get_secret_value
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


class DocxUpdate(BaseModel):
    """Схема для обновления/загрузки отчета"""

    token: str
    file: UploadFile
    filename: str
    replace_if_exist: bool


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
        token = JWT(token=values.get("token", ""))
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

    SecretType = Union[str, SecretStr]

    def __init__(self, token: str) -> None:
        self.token = token
        self._issuer = ""
        self._pub_key = ""
        self._algorithm = ""

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
        key = await get_key(f"public_keys/{self.issuer.lower()}.pub")
        return key

    @property
    def issuer(self) -> str:
        """Извлекает издателя токена"""
        # установим издателя токена, для этого прочитаем нагрузку без валидации.
        claimset_without_validation = jwt.decode(
            jwt=self.token, options={"verify_signature": False}
        )
        sanitize_issuer = str(sanitize_filepath(claimset_without_validation.get("iss", "")))
        return sanitize_issuer.strip().replace(".", "_").replace("-", "_")

    # @property
    async def decode_jwt(
        self,
        # payload: DocxCreate | DocxUpdate | JWToken,
        audience: str,
    ) -> dict[str, str]:
        try:
            # определяем наличие разрешения
            # token = JWT(token=payload.token)
            # log.info(config.PUBLIC_KEY)
            # log.info(config.PRIVATE_KEY)
            # log.debug(audience)
            # валидируем токен
            decoded_payload = jwt.decode(
                jwt=self.token,
                audience=audience,
                key=await self.pub_key,
                algorithms=[self.algorithm],
            )
            # log.debug("", o=decoded_payload)
            return decoded_payload
        except InvalidAudienceError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_AUD_NOT_FOUND.value)
        except ExpiredSignatureError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_EXPIRE.value)
        except ValueError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.INVALID_TOKEN.value)
        except DecodeError:
            raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT.value)

    def generate_jwt(
        self,
        data: dict,
        lifetime: timedelta | None = None,
        secret: SecretType = config.PRIVATE_KEY,
        algorithm: str = config.JWT_ALGORITHM,
    ) -> str:
        """only for tests"""
        if not lifetime:
            lifetime = timedelta(days=config.JWT_ACCESS_KEY_EXPIRES_TIME_DAYS)

        data["exp"] = datetime.utcnow() + lifetime
        # log.trace(data)
        payload = TokenCustomModel(**data)
        # log.debug(payload)
        return jwt.encode(
            payload=payload.dict(exclude_none=True),
            key=self.get_secret_value(secret),
            algorithm=algorithm,
        )

    def get_secret_value(self, secret: SecretType) -> str:
        if isinstance(secret, SecretStr):
            return secret.get_secret_value()
        return secret
