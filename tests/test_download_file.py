import pathlib

import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["docx-create", "docx-read"])])
async def test_download_file(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест скачивания готового файла"""

    username = "Васян Хмурый"
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    assert resp.status_code == 201
    resp = await client.get(
        routes.request_to_download_file(filename=data.get("url")),
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    assert resp.status_code == 200
    log.debug("", o=data)
    # зачистим артефакты
    pathlib.Path(data.get("filename")).unlink()
