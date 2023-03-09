import pathlib

from fastapi import FastAPI, Depends
from fastapi.types import DecoratedCallable
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.schemas import DocxCreate, DocxResponse


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
    resp = DocxResponse(
        filename=path_to_save,
        url=f"{config.DOWNLOADS_URL}/{payload.template}",
    )
    return resp


prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(router, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
