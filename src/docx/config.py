import asyncio
import pathlib
from functools import lru_cache
from typing import Sequence

from pydantic import BaseSettings, validator, HttpUrl
from logrich.logger_ import log  # noqa
from pydantic.fields import ModelField

from src.docx.helpers.tools import get_key

DOTENV_FILE = "./.env"


@lru_cache()
class Settings(BaseSettings):
    """
    Server config settings
    """

    class Config:
        env_file = DOTENV_FILE
        env_file_encoding = "utf-8"

    TEMPLATES_DIR: str = "templates"
    DOWNLOADS_DIR: str = "downloads"
    DOWNLOADS_URL: str = "downloads"

    ALGORITHMS_WHITE_LIST: Sequence[str] = ("ES256", "ES512", "PS256", "PS512", "EdDSA")

    @validator("DOWNLOADS_DIR")
    def create_downloads_dir(cls, v: str) -> str:
        """make place if not exist"""
        place = pathlib.Path(v)
        if not place.is_dir():
            place.mkdir()
        return v

    DEBUG: bool = False
    RELOAD: bool = False
    LOCAL: bool = False
    TESTING: bool = False

    API_PORT_INTERNAL: int = 8000
    API_HOSTNAME: str = "0.0.0.0"
    API_PATH_PREFIX: str = "/api/"
    API_VERSION: str = "v1"
    PROTOCOL_SCHEME: str = "http://"
    # ссылка на сайт, на странице /docs
    ROOT_URL: str = "/docs"

    @validator("ROOT_URL")
    def set_root_url(cls, value: str, values: dict, config: BaseSettings, field: ModelField) -> str:
        # log.debug(value)
        # log.debug('',o=values)
        # log.debug(config)
        # log.debug(field)
        # log.debug(cls)
        root_url: HttpUrl = HttpUrl(
            f'{values.get("API_HOSTNAME")}:{values.get("API_PORT_INTERNAL")}{value}',
            scheme=str(values.get("PROTOCOL_SCHEME")),
        )
        # return 'http://0.0.0.0:5000/docs'
        return f"{root_url.scheme}{root_url}"

    FILENAME_MIN_LENGTH: int = 3
    FILENAME_MAX_LENGTH: int = 100

    TEMPLATE_MIN_LENGTH: int = 3
    TEMPLATE_MAX_LENGTH: int = 100

    # ---------- только для тестов ----------
    JWT_ALGORITHM: str = "ES256"
    TOKEN_AUDIENCE: str | list[str] | None = "test-audience"
    PRIVATE_KEY: str = ""
    JWT_ACCESS_KEY_EXPIRES_TIME_DAYS: int = 3650

    @validator("PRIVATE_KEY")
    def set_private_key(
        cls, value: str, values: dict, config: BaseSettings, field: ModelField
    ) -> str | None:
        if values.get("TESTING"):
            privkey = asyncio.run(get_key(key="tests/priv-key.pem"))
            return privkey
        return None

    # ---------- только для тестов ----------

    LOG_LEVEL: int = 0


config = Settings()
