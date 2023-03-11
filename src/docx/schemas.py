from datetime import datetime
from typing import Annotated, Sequence, Dict
import pathlib

from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field, validator, EmailStr

from src.docx.config import config


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

    template: Annotated[
        str,
        Field(
            min_length=config.TEMPLATE_MIN_LENGTH,
            max_length=config.TEMPLATE_MAX_LENGTH,
            description="Имя заранее загруженного шаблона",
        ),
    ]

    @validator("template")
    def template_must_be_exist(cls, v: str) -> pathlib.Path:
        """make Path from string"""
        tpl_place = pathlib.Path(f"{config.TEMPLATES_DIR}/{v}")
        if not tpl_place.is_file():
            raise ValueError(f"Template {tpl_place} not exist!")
        return tpl_place

    token: str = Field(
        description="JWT подписанный асинхронным алгоритмом, при этом аудиенция токена должна соотвествовать аудиенции издателя указанной в переменных окружения данного сервиса. Издатель должен её определить и включить в токен перед запросом"
    )

    context: Dict[str, str] = Field(default={}, description="Переменные шаблона")


class DocxResponse(BaseModel):
    """схема для ответа на создание отчета"""

    filename: pathlib.Path
    url: str


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
        description="аудиенция, издатель должен её определить и включить в токен перед запросом."
    )
