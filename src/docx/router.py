import pathlib

from fastapi import FastAPI, Depends
from logrich.logger_ import log  # noqa
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.depends import check_access
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.schemas import DocxCreate, DocxResponse


router = APIRouter()


@router.post(
    "/create",
    response_model=DocxResponse,
    dependencies=[Depends(check_access)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.TOKEN_EXPIRE: {
                            "summary": "Срок действия токена вышел",
                            "value": {"detail": ErrorCodeLocal.TOKEN_EXPIRE},
                        },
                        ErrorCodeLocal.TOKEN_AUD_FAIL: {
                            "summary": "Поле aud не содержит корректного значения",
                            "value": {"detail": ErrorCodeLocal.TOKEN_AUD_FAIL},
                        },
                    }
                }
            },
        },
    },
)
async def create_docx(
    payload: DocxCreate,
) -> DocxResponse:
    """создать файл *.docx по шаблону"""
    # log.debug(access)

    doc = DocxTemplate(payload.template)
    doc.render(payload.context)
    path_to_save = pathlib.Path().cwd().joinpath(config.DOWNLOADS_DIR, f"{payload.filename}.docx")
    doc.save(path_to_save)

    resp = DocxResponse(
        filename=path_to_save,
        url=f"{config.DOWNLOADS_URL}/{payload.filename}.docx",
    )
    return resp


prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_router(app: FastAPI) -> None:
    app.include_router(router, prefix=f"{prefix}{__version__}/docx", tags=["Docx"])
