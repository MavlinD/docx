import uvicorn

from fastapi import FastAPI
from logrich.logger_ import errlog
from logrich.logger_assets import console
from rich.style import Style

# from config import config
from src.docx.router import init_router
from src.docx.config import config


def app() -> FastAPI:
    app_ = FastAPI(
        # **sw_params,
        # swagger_ui_parameters=sw_ui,
        # contact={
        #     "name": project["name"],
        #     "url": config.ROOT_URL,
        # },
        # openapi_tags=tags_metadata,
    )
    # try:
    #     app_.mount("/assets", StaticFiles(directory="wiki/site/assets"), name="static")
    # except Exception as err:
    #     log.warning(err)

    # init_err_handlers(app_)
    init_router(app_)
    # uncomment below if you need middleware
    # init_middleware(app_)

    return app_


@errlog.catch
def main() -> None:
    # console.rule(f"[green]{sw_params['title']}[/]", style=Style(color="magenta"))
    # asyncio.run(init_startup_events())
    uvicorn.run(
        "main:app",
        reload=config.RELOAD,
        factory=True,
        port=config.API_PORT_INTERNAL,
        host=config.API_HOSTNAME,
    )


if __name__ == "__main__":
    main()
