import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-crea"])])
async def test_cant_create_docx(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест создания docx с некорректной аудиенцией
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        headers=await auth_headers(audience=audience),
        json=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 403, "некорректный ответ сервера"
