import pathlib
from typing import Callable, Any

from docxtpl import DocxTemplate

from fastapi import FastAPI, Depends
from fastapi.types import DecoratedCallable
from fastapi import APIRouter as FastAPIRouter
from starlette import status

from config import config
from schemas import DocxCreate, DocxResponse


class APIRouter(FastAPIRouter):
    """compute trailing slashes in request"""

    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if path.endswith("/") and path != "/":
            path = path[:-1]

        add_path = super().api_route(path, include_in_schema=include_in_schema, **kwargs)
        alternate_path = path + "/"
        add_alternate_path = super().api_route(alternate_path, include_in_schema=False, **kwargs)

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            add_path(func)
            return add_alternate_path(func)

        return decorator


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
    # content = {"username": "Васян Хмурый", "place": "Кемерово"}
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
