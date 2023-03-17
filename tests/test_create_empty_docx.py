import pathlib

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-create"])])
async def test_create_empty_docx(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест создания пустого, незаполненного шаблона docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    token_issuer = "test-auth.site.com"
    token_data = {
        "iss": token_issuer,
        "aud": ["docx-create", "other-aud"],
    }
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=await auth_headers(audience=audience),
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("", o=data)
    assert resp.status_code == 201, "некорректный ответ сервера"
    out_file = pathlib.Path(data.get("filename"))

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
