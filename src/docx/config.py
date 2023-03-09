import pathlib
from functools import lru_cache
from pydantic import BaseSettings, validator
from logrich.logger_ import log  # noqa


DOTENV_FILE = "./.env"


@lru_cache()
class Settings(BaseSettings):
    """
    Server config settings
    """

    class Config:
        env_file = DOTENV_FILE
        env_file_encoding = "utf-8"

    TEMPLATES_DIR: str = "src/docx/templates"
    DOWNLOADS_DIR: str = "downloads"
    DOWNLOADS_URL: str = "downloads"

    @validator("DOWNLOADS_DIR", allow_reuse=True)
    def create_downloads_dir(cls, v: str) -> str:
        """make place if not exist"""
        place = pathlib.Path(v)
        if not place.is_dir():
            place.mkdir()
        return v

    DEBUG: bool = True
    RELOAD: bool = True
    LOCAL: bool = True
    TESTING: bool = True
    API_PORT_INTERNAL: int = 8000
    API_HOSTNAME: str = "0.0.0.0"
    API_PATH_PREFIX: str = "/api/"
    API_VERSION: str = "v2"

    FILENAME_MIN_LENGTH: int = 3
    FILENAME_MAX_LENGTH: int = 100

    TEMPLATE_MIN_LENGTH: int = 3
    TEMPLATE_MAX_LENGTH: int = 100

    LOG_LEVEL: int = 0


config = Settings()
