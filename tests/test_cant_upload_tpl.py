import pytest
from httpx import AsyncClient, Headers

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
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test-nsp")])
async def test_upload_tpl_with_over_max_size(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона с размером свыше ограничения"""

    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-update"])])
async def test_cant_upload_tpl_without_nsp(
    client: AsyncClient, routes: Routs, audience: str
) -> None:
    """тест невозможности загрузки шаблона без указания папки пользователя"""

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
    assert resp.status_code == 400, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test-nsp")])
async def test_cant_upload_tpl_without_iss(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест невозможности загрузки шаблона без указания издателя токена"""

    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience, token_issuer="", namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 400, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,token_issuer,namespace", [(["other-aud", "docx-update"], "fake-issuer", "test-nsp")]
)
async def test_cant_upload_tpl_with_fake_iss(
    client: AsyncClient, routes: Routs, audience: str, token_issuer: str, namespace: str
) -> None:
    """тест невозможности загрузки шаблона без указания издателя токена"""

    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(
            audience=audience, token_issuer=token_issuer, namespace=namespace
        ),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 400, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test-nsp")])
async def test_upload_tpl_with_not_allowed_ext(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона недопустимого типа"""

    payload: dict = {}
    path_to_file = "tests/files/lipsum.jpg"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422, "некорректный ответ сервера."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test-nsp")])
async def test_upload_tpl_without_replace(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона без замены существующего файла, для замены нужно указать нужный флаг"""

    # сначала загрузим шаблон
    template_name = "test-filename.docx"
    payload = {"filename": template_name, "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    headers: Headers = await auth_headers(audience=audience, namespace=namespace)
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера."

    # теперь запросим создание отчета

    payload = {
        "filename": template_name,
    }
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 409, "некорректный ответ сервера."
