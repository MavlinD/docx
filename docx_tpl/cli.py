from pprint import pprint

# import uvicorn
import uvicorn
from docxtpl import DocxTemplate
import argparse
import pathlib

from fastapi import FastAPI
from logrich.logger_ import errlog
from logrich.logger_assets import console
from rich.style import Style

from config import config
from router import init_router


def main_old():
    parser = argparse.ArgumentParser(description="Template engine for docx")
    parser.add_argument("--payload", type=str, help="Input dir for videos")
    parser.add_argument("filename", type=str, help="Имя сохраняемого файла")
    args = parser.parse_args()
    print(args.payload)
    BASE_DIR = pathlib.Path().resolve().parent
    doc = DocxTemplate("templates/my_word_template.docx")
    context = {"username": "Васян Хмурый", "place": "Кемерово"}
    doc.render(context)

    # p = pathlib.Path(__file__)
    # print(p)
    # print(pathlib.Path().cwd())
    # pprint(pathlib.Path().resolve().parent)
    # pprint(pathlib.Path().parent)
    # print(pathlib.Path().parent.absolute())
    doc.save(BASE_DIR.joinpath(f"{config.DOWNLOADS_DIR}/{args.filename}.docx"))


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
