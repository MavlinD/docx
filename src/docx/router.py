import os
import pathlib

import jwt
from fastapi import FastAPI, Depends
from fastapi.types import DecoratedCallable
from logrich.logger_ import log
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.helpers.tools import get_key
from src.docx.schemas import DocxCreate, DocxResponse
from dotenv import load_dotenv, dotenv_values

load_dotenv()

router = APIRouter()


# async def check_payload(payload):
#     yield DocxCreate(**payload)


@router.post(
    "/create",
    response_model=DocxResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_docx(
    payload: DocxCreate,
) -> DocxResponse:
    """создать файл *.docx по шаблону"""
    doc = DocxTemplate(payload.template)
    doc.render(payload.context)
    path_to_save = pathlib.Path().cwd().joinpath(config.DOWNLOADS_DIR, f"{payload.filename}.docx")
    doc.save(path_to_save)
    # log.debug(payload.token)
    # decoded = jwt.decode(encoded, public_key, algorithms=["RS256"])
    pub_key = await get_key(f"public_keys/{payload.issuer}.pub")
    # pub_key = await get_key(payload.issuer)
    # log.debug(pub_key)
    ISSUER = payload.issuer.upper()
    audience = os.getenv(f"TOKEN_AUDIENCE_{ISSUER}", "")
    algorithm = os.getenv(f"TOKEN_ALGORITHM_{ISSUER}", "")
    # log.info(config.PUBLIC_KEY)
    # log.info(config.PRIVATE_KEY)
    # log.debug(audience)
    # декодируем нагрузку пользовательского токена
    decoded_payload = jwt.decode(
        jwt=payload.token,
        audience=audience,
        key=pub_key,
        algorithms=[algorithm],
    )
    log.debug("", o=decoded_payload)

    resp = DocxResponse(
        filename=path_to_save,
        url=f"{config.DOWNLOADS_URL}/{payload.filename}.docx",
    )
    return resp


prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(router, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
