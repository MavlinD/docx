import asyncio
import functools
import locale
import pathlib
import re
import time
from contextlib import contextmanager
from datetime import datetime, date
from typing import Dict, List, Callable, Any, Generator
import hashlib
import json

import toml
from fastapi import FastAPI
from jwt import InvalidAudienceError, ExpiredSignatureError, DecodeError

from logrich.logger_ import log  # noqa
from pathvalidate import sanitize_filepath
from starlette.routing import Route
from transliterate import translit

from src.docx.exceptions import InvalidVerifyToken, ErrorCodeLocal

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


def sanity_str(string: str, language_code: str = "ru") -> str:
    """санитизирует и нормализует национальные алфавиты"""
    str_ = translit(
        str(sanitize_filepath(string)).replace(" ", "_").lower(),
        language_code=language_code,
        reversed=True,
    )
    str_ = re.sub("'|\"|@|%|#|$|&|\*|=", "", str_)  # noqa
    return str_


async def read_response(temp_file: str = "temp.txt") -> str:
    """читает ф-л с диска, исп-ся в тестах"""
    with open(temp_file, "r", encoding="utf-8") as fp:
        return fp.read()


@contextmanager
def wrapping_logic_timer(func_name: str) -> Generator:
    """время выполнения кода"""
    tic = time.perf_counter()
    yield
    toc = time.perf_counter()
    format_time = f"{toc - tic:0.3f} sec."
    log.trace(f"[green]{func_name}:[/] {format_time}")


def duration(func: Callable) -> Callable:
    """декорирует временем выполнения вызываюший код"""

    def timing_context() -> Any:
        return wrapping_logic_timer(func.__name__)

    return decorate_sync_async(decorating_context=timing_context, func=func)


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


async def get_key(key: str) -> str:
    """получим ключ из файла на диске"""
    path_to_key = pathlib.Path(key)
    with open(path_to_key, mode="r", encoding="utf-8") as f:
        return f.read().strip()


async def get_file(path: str, mode: str = "r") -> bytes | str:
    """вернет файл на диске"""
    path_to_key = pathlib.Path(path)
    with open(path_to_key, mode=mode, buffering=0) as f:
        return f.read()


def get_project() -> Dict:
    """return project file"""
    pyproject = toml.load(open(pathlib.Path("pyproject.toml")))
    return pyproject["tool"]["poetry"]


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def print_routs(app: FastAPI) -> None:
    """print all app routs"""
    for route in app.router.routes:
        if isinstance(route, Route):
            log.trace(route.path)


@contextmanager
def wrapping_jwt_decode() -> Generator:
    """Проверка токена с обработкой исключений"""
    try:
        yield
    except InvalidAudienceError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_AUD_NOT_FOUND.value)
    except ExpiredSignatureError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_EXPIRE.value)
    except DecodeError:
        raise InvalidVerifyToken(msg=ErrorCodeLocal.TOKEN_NOT_ENOUGH_SEGMENT.value)


def decorate_sync_async(decorating_context: Callable, func: Callable) -> Callable:
    """Применяет декорации как к синхронному так и асинхронному коду"""
    # https://n8henrie.com/2021/11/decorator-to-memoize-sync-or-async-functions-in-python/
    # https://stackoverflow.com/questions/44169998/how-to-create-a-python-decorator-that-can-wrap-either-coroutine-or-function
    if asyncio.iscoroutinefunction(func):

        async def decorated(*args: list, **kwargs: dict) -> Any:
            with decorating_context():
                return await func(*args, **kwargs)

    else:

        def decorated(*args, **kwargs):  # type: ignore
            with decorating_context():
                return func(*args, **kwargs)

    return functools.wraps(func)(decorated)


def jwt_exception(func: Callable) -> Callable:
    """Декорирует проверку токена обработкой исключений"""
    return decorate_sync_async(decorating_context=wrapping_jwt_decode, func=func)
