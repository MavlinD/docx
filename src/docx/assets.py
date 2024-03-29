from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable
from logrich.logger_ import log  # noqa

from src.docx.config import config
from src.docx.exceptions import PathToTemplateNotExist, FileIsExist


class APIRouter(FastAPIRouter):
    """compute trailing slashes in request"""

    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if path.endswith("/") and path != "/":
            path = path[:-1]
        # log.debug(path)
        add_path = super().api_route(path, include_in_schema=include_in_schema, **kwargs)
        alternate_path = path + "/"
        add_alternate_path = super().api_route(alternate_path, include_in_schema=False, **kwargs)

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            add_path(func)
            return add_alternate_path(func)

        return decorator


def get_template(issuer: str, nsp: str | Path, template: str | Path) -> Path:
    # log.trace(config.TEMPLATES_DIR)
    # log.trace(issuer)
    # log.trace(template)
    path_to_template = Path(f"{config.TEMPLATES_DIR}/{issuer}/{nsp}/{template}")
    if not path_to_template.is_file():
        raise PathToTemplateNotExist(msg=str(path_to_template))
    return path_to_template


async def check_file_exist(name: Path, replace_if_exist: bool) -> None:
    """Проверяет существование файла для записи, вызывает исключение"""
    if Path(name).is_file():
        if not replace_if_exist:
            raise FileIsExist(msg=str(name))
