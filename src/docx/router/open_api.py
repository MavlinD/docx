from fastapi import FastAPI
from fastapi.routing import APIRoute
from logrich.logger_ import log  # noqa
from typing import Optional, Dict, Any, Callable
from starlette.responses import HTMLResponse

from fastapi.openapi.docs import get_swagger_ui_html
from src.docx.assets import APIRouter

router = APIRouter()


def custom_get_swagger_ui_html(
    *, openapi_url: str, title: str, swagger_ui_parameters: Optional[Dict[str, Any]] = None
) -> HTMLResponse:
    """wrapper for swagger_ui_html"""
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_css_url="assets/custom.css",
        swagger_ui_parameters=swagger_ui_parameters,
    )


sw_ui = {"defaultModelsExpandDepth": -1}


def set_open_api(app: FastAPI) -> Callable:
    """custom endpoint for docs"""

    async def swagger_ui_html():
        return custom_get_swagger_ui_html(
            openapi_url=app.openapi_url,
            swagger_ui_parameters=sw_ui,
            title=app.title + " - Swagger UI",
        )

    return swagger_ui_html


def reset_open_api(app: FastAPI) -> None:
    """replace standard api docs endpoint"""
    for route in app.router.routes:
        if route.path == "/docs":
            app.routes.remove(route)
            app.routes.append(
                APIRoute(path="/docs", endpoint=set_open_api(app), include_in_schema=False)
            )
