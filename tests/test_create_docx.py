import pathlib
from datetime import timedelta

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-create"])])
async def test_create_docx(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест создания docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    username = "Васян Хмурый"
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    headers: Headers = await auth_headers(audience=audience)
    # log.debug(dir(headers))
    # log.debug(headers.values())
    # log.debug(headers.get("Authorization"))
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 201, "некорректный ответ сервера"
    out_file = pathlib.Path(data.get("filename"))

    assert out_file.is_file(), "итоговый файл не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert username in " ".join(content), "данных в итоговом файле не наблюдается"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["docx-super"])])
async def test_create_jwt(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест создания jwt"""
    headers: Headers = await auth_headers(audience=audience, lifetime=timedelta(days=3650))
    print(headers.get("Authorization"))


#     eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0LWF1dGguc2l0ZS5jb20iLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxOTk0ODE5MDgxLCJhdWQiOlsiZG9jeC1zdXBlciJdfQ.nDpRlfCJlZK6MwsQERyZQfsztqNC8_MKuYApyS2IWwBEjkw3lQ7ne6OyG6qvHQS7dB2JRy_uJuJDDjswQYVWuA
