import asyncio
from pathlib import Path
from functools import lru_cache
from types import MappingProxyType
from typing import Sequence

from pydantic import BaseSettings, validator, HttpUrl, SecretStr
from logrich.logger_ import log  # noqa
from pydantic.fields import ModelField
from starlette.templating import Jinja2Templates

from src.docx.helpers.tools import get_key

DOTENV_FILE = "./.env"
templates = Jinja2Templates(directory="wiki/site")

# immutable dict
CONTENT_TYPE_WHITE_LIST = MappingProxyType(
    {
        "*.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        # "*.png": "image/png",
    },
)


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

    @property
    def content_type_white_list(self) -> dict[str, str]:
        """Список разрешенных форматов сохраняемых файлов."""
        return dict(CONTENT_TYPE_WHITE_LIST)

    @validator("DOWNLOADS_DIR", allow_reuse=True)
    def create_downloads_dir(cls, v: str) -> str:
        """make place if not exist"""
        place = Path(v)
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

    FILENAME_MIN_LENGTH: int = 3
    FILENAME_MAX_LENGTH: int = 100

    TEMPLATE_MIN_LENGTH: int = 3
    TEMPLATE_MAX_LENGTH: int = 100

    # максимальный размер загружаемого файла, Mb
    FILE_MAX_SIZE: float = 1

    # ---------- только для тестов ----------
    JWT_ALGORITHM: str = "ES256"
    TOKEN_AUDIENCE: str | list[str] | None = "test-audience"
    PRIVATE_KEY: SecretStr = SecretStr("")
    JWT_ACCESS_KEY_EXPIRES_TIME_DAYS: int = 3650
    TEST_ISSUER: str = "test-auth.site.com"

    @validator("PRIVATE_KEY", allow_reuse=True)
    def set_private_key(
        cls, value: str, values: dict, config: BaseSettings, field: ModelField
    ) -> SecretStr | None:
        if values.get("TESTING"):
            privkey = SecretStr(asyncio.run(get_key(key="tests/priv-key.pem")))
            return privkey
        return None

    # ---------- только для тестов ----------

    LOG_LEVEL: int = 0


config = Settings()
