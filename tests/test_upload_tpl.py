import json
import os
import pathlib

import pytest
from _pytest import monkeypatch
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.docx.config import config
from src.docx.helpers.security import generate_jwt
from src.docx.helpers.tools import get_file
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_upload_tpl(client: AsyncClient, routes: Routs) -> None:
    """тест загрузки шаблонов"""
    # envs = {"FILE_MAX_SIZE": "0.001"}
    # monkeypatch.setattr(os, "environ", envs)
    # monkeypatch.setenv("FILE_MAX_SIZE", "0.001")
    # log.debug(os.getenv("FILE_MAX_SIZE"))
    # config.FILE_MAX_SIZE = 0.001
    # username = "Васян Хмурый"
    token_issuer = "test-auth.site.com"
    token_data = {
        "iss": token_issuer,
        "aud": ["other-aud51=11311", "docx-update"],
    }
    token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "token": token,
    }
    file = "tests/files/lipsum2_article.jpg"
    file = ("file", open(file, "rb"))
    resp = await client.post(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        # data={"payload": payload},
        # params={"name": "xxxx"},
        # content={"name": "xxxx"},
        # json={"name": "xxxx="},
        # data={"name": "foo111", "point": 0.13, "is_accepted": False}
        # data={"name": "foo", "point": 0.13, "is_accepted": False}
        #     "filename": ["file1", "file22"],
        # data=json.dumps(
        #     {
        #         "filename": json.dumps(["file1", "file22"]),
        #         "token": token,
        #     }
        # )
        # params={
        # filename="file1"
        #     #     "data": json.dumps(
        #     #         {
        #     "token": token,
        #     #         }
        #     #     )
        # },
        # token=token,
        # data={"data": '{"filename": "foo111", "token": 0.13, "is_accepted": false}'}
        # data={"data": json.dumps({"name": "foo", "point": 0.13, "is_accepted": False})} # !!!
        # data={"data": {"name": "foo111", "point": 0.13, "is_accepted": False}}
        # data={"data": {"filename": "foo111", "point": 0.13, "is_accepted": False}}
        # data={"model": json.dumps({"foo": "111", "baz": 222})}
        # data={"model": json.dumps({"foo": "111", "baz": 222})}
        # data={"model": {"foo": "111", "baz": 222}}
        # data={"foo": "111", "baz": 222}
        # data={"name": "x1313xxx-"},
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("", o=data)
    return
    assert resp.status_code == 201, "некорректный ответ сервера"
    out_file = pathlib.Path(data.get("filename"))

    assert out_file.is_file(), "итоговый файл не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert username in " ".join(content), "данных в итоговом файле не наблюдается"
