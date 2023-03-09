from typing import Annotated
import pathlib

from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field, validator

from src.docx.config import config


class DocxCreate(BaseModel):
    """схема для создания отчета"""

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
            description="Имя шаблона",
        ),
    ]

    @validator("template")
    def template_must_be_exist(cls, v: str) -> pathlib.Path:
        """make Path from string"""
        tpl_place = pathlib.Path(f"{config.TEMPLATES_DIR}/{v}")
        if not tpl_place.is_file():
            raise ValueError(f"Template {tpl_place} not exist!")
        return tpl_place

    context: dict = {}


class DocxResponse(BaseModel):
    """схема для ответа на создание отчета"""

    filename: pathlib.Path
    url: str
