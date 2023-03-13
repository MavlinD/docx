import pathlib
from typing import Any, Callable

from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable
from logrich.logger_ import log  # noqa

from src.docx.config import config
from src.docx.exceptions import PathToTemplateNotExist


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


def get_template(issuer: str, template: str) -> pathlib.Path:
    log.trace(config.TEMPLATES_DIR)
    log.trace(issuer)
    log.trace(template)
    path_to_template = pathlib.Path(f"{config.TEMPLATES_DIR}/{issuer}/{template}")
    if not path_to_template.is_file():
        raise PathToTemplateNotExist(msg=str(path_to_template))
    return path_to_template
