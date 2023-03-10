import uvicorn

from fastapi import FastAPI
from logrich.logger_ import errlog
from logrich.logger_assets import console
from rich.style import Style

from src.docx.helpers.tools import get_project
from src.docx.err_handlers import init_err_handlers  # noqa
from src.docx.middleware import init_middleware  # noqa
from src.docx.router import init_router
from src.docx.config import config


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
        "description": "Основные действия с шаблонизатором",
    },
]


def app() -> FastAPI:
    app_ = FastAPI(
        **sw_params,
        swagger_ui_parameters=sw_ui,
        contact={
            "name": project["name"],
            "url": config.ROOT_URL,
        },
        openapi_tags=tags_metadata,
    )
    init_router(app_)
    # uncomment below if you need custom err handlers
    # init_err_handlers(app_)
    # uncomment below if you need middleware
    # init_middleware(app_)

    return app_


@errlog.catch
def main() -> None:
    console.rule(
        f"[green]{sw_params['title']}:{sw_params['version']}[/]", style=Style(color="magenta")
    )
    uvicorn.run(
        "main:app",
        reload=config.RELOAD,
        factory=True,
        port=config.API_PORT_INTERNAL,
        host=config.API_HOSTNAME,
    )


if __name__ == "__main__":
    main()
