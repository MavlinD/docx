import pathlib
from datetime import timedelta

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.docx.config import config
from src.docx.helpers.security import generate_jwt
from src.docx.schemas import TokenCustomModel
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_docx(
    client: AsyncClient,
    routes: Routs,
) -> None:
    """тест создания docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    username = "Васян Хмурый"
    token_data = {
        "sub": "test",
        "email": EmailStr("test@loc.loc"),
    }
    token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "my_word_template.docx",
        "context": {"username": username, "place": "Кемерово"},
        "token": token,
        "issuer": "auth_v2",
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
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
    assert username in " ".join(content), "данных в итоговом файле не наблюдается"
