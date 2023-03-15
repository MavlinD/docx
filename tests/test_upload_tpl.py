import pathlib

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from src.docx.helpers.security import generate_jwt
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_upload_tpl(client: AsyncClient, routes: Routs) -> None:
    """тест загрузки шаблона"""
    # config.FILE_MAX_SIZE = 0.001
    token_issuer = "test-auth.site.com"
    token_data = {
        "iss": token_issuer,
        "aud": ["other-aud", "docx-update"],
    }
    token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {
        "filename": "temp_dir/test-filename.docx",
        "token": token,
    }
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.post(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера"
    out_file = pathlib.Path(data.get("template"))

    assert out_file.is_file(), "Шаблон не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert "Здравствуй мир!" in " ".join(content), "данных в итоговом файле не наблюдается"
