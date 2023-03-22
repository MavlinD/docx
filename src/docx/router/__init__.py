from fastapi import FastAPI

from src.docx.config import config
from .home import router as home
from .docx import router as docx

prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(docx, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
    app.include_router(home, prefix="")
