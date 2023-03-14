import json
import pathlib

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.docx.helpers.security import generate_jwt
from src.docx.helpers.tools import get_file
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_upload_tpl(
    client: AsyncClient,
    routes: Routs,
) -> None:
    """тест загрузки шаблонов"""
    # username = "Васян Хмурый"
    token_issuer = "test-auth.site.com"
    token_data = {
        "iss": token_issuer,
        "aud": ["other-aud", "docx-update"],
    }
    token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {
        #     "filename": "test-filename",
        #     "template": "test_docx_template.docx",
        #     "context": {"username": username, "place": "Кемерово"},
        "token": token,
    }
    file = "tests/files/nginx.png"
    file2 = "tests/files/lipsum1.jpg"
    files = [
        # "token": token,
        ("files", open(file, "rb")),
        ("files", open(file2, "rb")),
        # ("name", "test"),
        # ("file", open(file, "rb")),
        # ("file2", open(file2, "rb")),
    ]
    # payload["files"] = files
    resp = await client.post(
        routes.request_to_upload_template,
        # json={"name": "xxxx"},
        # json=payload,
        files=files,
        # data=payload,
        # params={"name": "xxxx"},
        # content={"name": "xxxx"},
        # json={"name": "xxxx="},
        # data={"name": "foo111", "point": 0.13, "is_accepted": False}
        # data={"name": "foo", "point": 0.13, "is_accepted": False}
        data={
            #     "filename": ["file1", "file22"],
            "filename": json.dumps(["file1", "file2"]),
            "token": token,
        }
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
