import pathlib

from fastapi import FastAPI, Depends
from logrich.logger_ import log  # noqa
from starlette import status
from docxtpl import DocxTemplate

from src.docx.assets import APIRouter
from src.docx.config import config
from src.docx.depends import check_create_access
from src.docx.exceptions import ErrorModel, ErrorCodeLocal
from src.docx.schemas import DocxCreate, DocxResponse


router = APIRouter()


@router.post(
    "/create",
    response_model=DocxResponse,
    dependencies=[Depends(check_create_access)],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.TOKEN_EXPIRE: {
                            "summary": "Срок действия токена вышел.",
                            "value": {"detail": ErrorCodeLocal.TOKEN_EXPIRE},
                        },
                        ErrorCodeLocal.TOKEN_AUD_FAIL: {
                            "summary": "Поле aud не содержит корректного значения.",
                            "value": {"detail": ErrorCodeLocal.TOKEN_AUD_FAIL},
                        },
                        ErrorCodeLocal.TOKEN_AUD_NOT_FOUND: {
                            "summary": "Действие требует определённой аудиенции.",
                            "value": {"detail": ErrorCodeLocal.TOKEN_AUD_NOT_FOUND},
                        },
                        ErrorCodeLocal.TOKEN_AUD_NOT_ALLOW: {
                            "summary": "Запрошенная в токене аудиенция не разрешена, установите соотвествующую переменную окружения.",
                            "value": {"detail": ErrorCodeLocal.TOKEN_AUD_NOT_ALLOW},
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
    """Создать файл *.docx по шаблону"""

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
