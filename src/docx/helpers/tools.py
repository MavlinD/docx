import functools
import locale
import pathlib
import time
from datetime import datetime, date
from typing import Dict, List, Callable, Any, BinaryIO
import hashlib
import json

import toml

from logrich.logger_ import log  # noqa

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


async def read_response(temp_file: str = "temp.txt") -> str:
    """читает ф-л с диска, исп-ся в тестах"""
    with open(temp_file, "r", encoding="utf-8") as fp:
        return fp.read()


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
