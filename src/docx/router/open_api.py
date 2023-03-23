import json

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import swagger_ui_default_parameters
from fastapi.routing import APIRoute
from logrich.logger_ import log  # noqa
from typing import Optional, Dict, Any, Callable
from starlette.responses import HTMLResponse

from src.docx.assets import APIRouter

router = APIRouter()


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url: Optional[str] = None,
    init_oauth: Optional[Dict[str, Any]] = None,
    swagger_ui_parameters: Optional[Dict[str, Any]] = None,
    custom_js_url: str = "",
) -> HTMLResponse:
    """
    todo если swagger обновится, то нужно синхронизировать эту функцию
    """
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(jsonable_encoder(value))},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += f"""
    </script>
    </body>
    <script src="{custom_js_url}"></script>
    </html>
    """
    return HTMLResponse(html)


def custom_get_swagger_ui_html(
    *, openapi_url: str, title: str, swagger_ui_parameters: Optional[Dict[str, Any]] = None
) -> HTMLResponse:
    """wrapper for swagger_ui_html"""
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        custom_js_url="static/custom.js",
        swagger_css_url="static/bundle.css",
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
