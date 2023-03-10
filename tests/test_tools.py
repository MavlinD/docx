from fastapi import FastAPI
from httpx import Request
from logrich.logger_ import log
from requests import Response


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


@log.catch
def check_resp(resp: Response, status_code: int, print_: bool = False) -> dict | None:
    """проверяет утверждение и печатает ответ"""
    assert resp.status_code == status_code, resp.content.decode()
    data = None
    if resp.content:
        data = resp.json()
        if print_ and data:
            match str(type(data)):
                case "<class 'dict'>":
                    log.debug("", o=data)
                case "<class 'list'>":
                    for _ in data:
                        if type(_) is dict:
                            log.debug("", o=_)
    return data
