import uvicorn

from fastapi import FastAPI
from logrich.logger_ import errlog, log
from logrich.logger_assets import console
from rich.style import Style
from starlette.staticfiles import StaticFiles

from src.docx.helpers.tools import get_project
from src.docx.err_handlers import init_err_handlers  # noqa
from src.docx.middleware import init_middleware  # noqa
from src.docx.router import init_router
from src.docx.config import config

from src.docx.router.open_api import reset_open_api

project = get_project()

sw_params = {
    "title": project["name"],
    "version": project["version"],
    "description": f'<h4>{project["description"]}<br>Micro-service unit.</h4>',
    "debug": config.DEBUG,
}

sw_ui = {"defaultModelsExpandDepth": -1}

tags_metadata = [
    {
        "name": "Docx",
        "description": "Действия с шаблонизатором.",
    },
]


def run_app() -> FastAPI:
    app = FastAPI(
        **sw_params,
        swagger_ui_parameters=sw_ui,
        contact={
            "name": project["name"],
            "url": config.ROOT_URL,
        },
        openapi_tags=tags_metadata,
    )
    try:
        app.mount("/assets", StaticFiles(directory="wiki/site/assets"), name="static")

    except Exception as err:
        log.warning(err)

    reset_open_api(app)
    init_router(app)
    # print_routs(app)

    return app


@errlog.catch
def main() -> None:
    console.rule(
        f"[green]{sw_params['title']}:{sw_params['version']}[/]", style=Style(color="magenta")
    )
    uvicorn.run(
        "main:run_app",
        reload=config.RELOAD,
        factory=True,
        port=config.API_PORT_INTERNAL,
        host=config.API_HOSTNAME,
    )


if __name__ == "__main__":
    if config.TESTING or config.DEBUG:
        log.warning(
            "отключите режим тестирования и отладки - установите переменную TESTING=0 и DEBUG=0"
        )
        exit(128)

    main()
