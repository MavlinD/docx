import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

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
    """тест создания docx"""
    payload = {
        "filename": "test-filename",
        "template": "my_word_template.docx",
        "context": {"username": "Васян Хмурый", "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 201
