import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-create"], "")])
async def test_cant_create_docx_with_empty_nsp(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест невозможности создания docx с пустым nsp"""
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        headers=await auth_headers(audience=audience, namespace=namespace),
        json=payload,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 400, "некорректный ответ сервера"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-create"], "nsp-1,nsp-2")])
async def test_cant_create_docx_with_multiply_nsp(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест невозможности создания docx со множественным nsp"""
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        headers=await auth_headers(audience=audience, namespace=namespace),
        json=payload,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 400, "некорректный ответ сервера"
