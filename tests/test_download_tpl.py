from pathlib import Path

import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from src.docx.helpers.tools import duration
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-read"], "test-nsp")])
async def test_download_tpl(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест скачивания шаблона"""

    filename = "test_docx_template_to_upload.docx"
    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = f"tests/files/{filename}"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=("docx-update",), namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 201

    resp = await client.get(
        routes.request_to_download_template(filename=filename),
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    # print(resp.content)
    # data = resp.json()
    path = Path(f"templates/test_auth_site_com/{namespace}/{filename}")
    # log.debug(len(resp.content))
    assert len(resp.content) == path.stat().st_size
    log.trace(resp.elapsed)
    assert resp.status_code == 200
    # здесь отправленный файл не сохраняется в папке downloads


@duration
@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience, namespace", [(["other-aud", "docx-read"], "test-nsp")])
async def test_cant_download_tpl(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест скачивания несуществующего шаблона"""

    filename = "fake_template.docx"
    resp = await client.get(
        routes.request_to_download_template(filename=filename),
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    # log.debug(resp.text)
    log.debug(resp)
    # log.debug(resp.content.detail)
    # log.trace(resp.elapsed)
    assert resp.status_code == 404
