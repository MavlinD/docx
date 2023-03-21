from pathlib import Path

import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-read"])])
async def test_download_tpl(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест скачивания шаблона"""

    filename = "test_docx_template.docx"
    resp = await client.get(
        routes.request_to_download_template(filename=filename),
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    path = Path(f"templates/test_auth_site_com/{filename}")
    # log.debug(len(resp.content))
    assert len(resp.content) == path.stat().st_size
    log.trace(resp.elapsed)
    assert resp.status_code == 200


# @async_timer
@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-read"])])
async def test_cant_download_tpl(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест скачивания несуществующего шаблона"""

    filename = "fake_template.docx"
    resp = await client.get(
        routes.request_to_download_template(filename=filename),
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp.text)
    log.debug(resp)
    # log.debug(resp.content.detail)
    log.trace(resp.elapsed)
    assert resp.status_code == 404
