from typing import Annotated
import pathlib

from pydantic import BaseModel, Field, validator

from config import config


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
    def template_must_be_exist(cls, v: str) -> str:
        tpl_exists = pathlib.Path(f"templates/{v}").is_file()
        if not tpl_exists:
            raise ValueError("Template not exist!")
        return v

    context: dict = {}


class DocxResponse(BaseModel):
    """схема для ответа на создание отчета"""

    filename: pathlib.Path
    # filename: str
    url: str
