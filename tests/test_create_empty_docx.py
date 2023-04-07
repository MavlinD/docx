import pathlib

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from starlette.datastructures import Headers

from src.docx.config import config
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["other-aud", "docx-create", "docx-update"], "test_nsp")]
)
async def test_create_empty_docx(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест создания пустого, незаполненного шаблона docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    # сначала загрузим шаблон
    template_name = "test-filename.docx"
    payload = {"filename": template_name, "replace_if_exist": True}
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
    # теперь запросим создание отчета
    payload = {
        "filename": "test-filename",
        "template": template_name,
        "context": {},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
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
    assert {
        "",
        "Здравствуй мир!",
        "Я живу в .",
        "Меня зовут .",
    } == content, "итоговый файл таки изменился"
    # зачистим артефакты
    out_file.unlink()
