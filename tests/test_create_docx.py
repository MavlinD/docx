import pathlib
from datetime import timedelta

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa

from src.docx.config import config
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["other-aud", "docx-create", "docx-update"], "test-nsp")]
)
async def test_create_docx(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест создания docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    # сначала загрузим шаблон
    payload = {"filename": "test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    headers: Headers = await auth_headers(audience=audience, namespace=namespace)
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера."

    username = "Васян Хмурый"
    payload = {
        "filename": "test-filename",
        "template": "test-filename.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера"
    out_file = pathlib.Path(
        f'{config.DOWNLOADS_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("url")}'
    )

    assert out_file.is_file(), "итоговый файл не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert username in " ".join(content), "данных в итоговом файле не наблюдается"
    # return
    # зачистим артефакты
    out_file.unlink()


@pytest.mark.skipif(skip, reason="tool test")
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["docx-super"])])
async def test_create_jwt(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест создания jwt"""
    headers: Headers = await auth_headers(audience=audience, lifetime=timedelta(days=3650))
    log.debug(headers.get("Authorization"))
