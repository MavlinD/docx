import pathlib

from fastapi import FastAPI, Depends
from fastapi.types import DecoratedCallable
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.schemas import DocxCreate, DocxResponse


router = APIRouter()


async def check_payload(payload):
    yield DocxCreate(**payload)


@router.post(
    "/create",
    response_model=DocxResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_docx(
    payload: DocxCreate,
) -> DocxResponse:
    """создать файл *.docx по шаблону"""
    tpl = f"templates/{payload.template}"
    doc = DocxTemplate(tpl)
    context = payload.context
    doc.render(context)
    BASE_DIR = pathlib.Path().resolve().parent
    doc.save(BASE_DIR.joinpath(f"{config.DOWNLOADS_DIR}/{payload.filename}.docx"))
    resp = DocxResponse(
        filename=pathlib.Path(f"{config.DOWNLOADS_DIR}/{payload.filename}.docx"),
        url=f"{config.DOWNLOADS_URL}/{payload.template}",
    )
    return resp


prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(router, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
