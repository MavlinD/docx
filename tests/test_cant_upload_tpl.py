import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa
from override_settings import async_override_settings

from src.docx.config import config
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@async_override_settings(settings=config, FILE_MAX_SIZE=0.00000001)
@pytest.mark.parametrize("audience", [(["other-aud", "docx-update"])])
async def test_upload_tpl_with_over_max_size(
    client: AsyncClient, routes: Routs, audience: str
) -> None:
    """тест загрузки шаблона с размером свыше ограничения"""

    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-update"])])
async def test_upload_tpl_with_not_allowed_ext(
    client: AsyncClient, routes: Routs, audience: str
) -> None:
    """тест загрузки шаблона недопустимого типа"""

    payload: dict = {}
    path_to_file = "tests/files/lipsum.jpg"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-update"])])
async def test_upload_tpl_without_replace(
    client: AsyncClient, routes: Routs, audience: str
) -> None:
    """тест загрузки шаблона без замены существующего файла, для замены нужно указать нужный флаг"""

    payload: dict = {}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 409, "некорректный ответ сервера."
