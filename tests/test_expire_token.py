import pytest
from httpx import AsyncClient

from datetime import timedelta
from logrich.logger_ import log  # noqa
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-create"])])
async def test_expire_token(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест невозможности создания docx с просроченным токеном
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
        headers=await auth_headers(audience=audience, lifetime=timedelta(days=-1)),
        json=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    assert resp.status_code == 403, "некорректный ответ сервера"
