import os
import toml
from typing import Any, Callable, Dict

from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable
from logrich.logger_ import log  # noqa


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


def get_project() -> Dict:
    """return project file"""
    BASE_DIR = os.path.dirname(__file__)
    pyproject = toml.load(open(os.path.join(BASE_DIR, "..", "..", "pyproject.toml")))
    return pyproject["tool"]["poetry"]


def get_key(key: str) -> str:
    """получим ключ из файла на диске"""
    BASE_DIR = os.path.dirname(__file__)
    with open(os.path.join(BASE_DIR, key), mode="r", encoding="utf-8") as f:
        return f.read().strip()
