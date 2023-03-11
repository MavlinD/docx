import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.docx.helpers.security import generate_jwt
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_docx(
    client: AsyncClient,
    routes: Routs,
) -> None:
    """тест создания docx
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    username = "Васян Хмурый"
    token_issuer = "test-auth.site.com"
    token_data = {
        "iss": token_issuer,
        "aud": ["fake-create", "other-aud"],
    }
    token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
        "token": token,
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 403, "некорректный ответ сервера"
