import functools
import hashlib
import locale
import time
from datetime import datetime, date
from typing import Dict, List, Callable

from fastapi import FastAPI
from httpx import Request
from requests import Response

from logrich.logger_ import log  # noqa

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


def print_endpoints(app: FastAPI) -> None:
    """печать всех доступных конечных точек"""
    log.debug(type(app.routes))
    for rout in app.routes:
        log.info(
            f"[#EE82EE]{str(next(iter(rout.methods))) + ':':<7}[/][#ADFF2F]{rout.path}:[/] [#FF4500]{rout.name}[/]"  # type: ignore
        )


async def print_request(request: Request) -> None:
    """
    исп-ю в тестах
    https://www.python-httpx.org/api/
    """
    log.info(f"[#EE82EE]{str(request.method) + ':':<8}[/]{request.url.raw_path.decode('UTF-8')}")


async def read_response(temp_file: str = "temp.txt") -> str:
    """читает ф-л с диска, исп-ся в тестах"""
    with open(temp_file, "r", encoding="utf-8") as fp:
        return fp.read()


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


def timer(func: Callable) -> Callable:
    """
    декоратор, определяет время выполнения
    @rtype: str
    """

    @functools.wraps(func)
    def wrapper_timer(*args: List, **kwargs: Dict) -> Callable:
        name = func.__name__
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        ln = len(name) + 15
        format_time = f"{elapsed_time:0.3f} seconds"
        print("-" * ln)
        print("\033[0;38;5;211m" + f"{name}: {format_time}")
        print("-" * ln)
        if value:
            value["elapsed_time"] = format_time
        return value

    return wrapper_timer


def get_quarter(_date: date) -> int:
    """возвращает квартал"""
    return round((_date.month - 1) / 3 + 1)


def get_date(
    _date: str, date_format_in: str = "%Y-%m-%dT%H:%M:%S.%fZ", default: object = None
) -> object:
    """делает из строки времени объект времени либо то, что требуется"""
    dt = default
    try:
        dt = datetime.strptime(_date, date_format_in)
        return dt
    except Exception:
        return dt


def crc(*args: List) -> str:
    """возвращает контрольную сумму в виде MD5 хеша"""
    _hash = hashlib.md5(str([args]).encode("utf-8"))
    return _hash.hexdigest()


def set_to_obj(arg: str | List) -> Dict:
    """рекурсивное создание объекта из строки вида 'foo.bar.baz'"""
    resp = {}
    if type(arg) == str:
        _arg = arg.split(".")
        return set_to_obj(_arg)
    if len(arg) > 1:
        resp[arg[0]] = set_to_obj(arg[1:])
        return resp
    resp[arg[0]] = {}
    return resp
