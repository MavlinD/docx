from pathlib import Path

from fastapi import FastAPI
from httpx import Request
from logrich.logger_ import log


async def print_request(request: Request) -> None:
    """
    исп-ю в тестах
    https://www.python-httpx.org/api/
    """
    log.info(f"[#EE82EE]{str(request.method) + ':':<8}[/]{request.url.raw_path.decode('UTF-8')}")


def print_endpoints(app: FastAPI) -> None:
    """печать всех доступных конечных точек"""
    log.debug(type(app.routes))
    for rout in app.routes:
        log.info(
            f"[#EE82EE]{str(next(iter(rout.methods))) + ':':<7}[/][#ADFF2F]{rout.path}:[/] [#FF4500]{rout.name}[/]"  # type: ignore
        )


async def is_empty(folder: Path) -> bool:
    """check folder for empty"""
    # log.debug(folder)
    # log.info(folder.stat().st_size)
    return not any(folder.iterdir())


async def purge_dir(path: str, glob: str = "**/*", execute: bool = False) -> None:
    """purge dir from empty folders"""
    for p in Path(path).rglob(glob):
        if p.is_dir() and not p.is_file():
            if await is_empty(p):
                if execute:
                    # log.trace(p)
                    p.rmdir()


async def purge_files(path: str, glob: str = "*", execute: bool = False) -> None:
    """purge dir from files"""
    for node in Path(path).rglob(glob):
        if node.is_file():
            if execute:
                # log.trace(f"удаляю: {node}")
                node.unlink()
