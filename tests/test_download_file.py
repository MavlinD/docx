import pytest
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["docx-create", "docx-read", "docx-update"], "test-nsp")]
)
async def test_download_file(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест скачивания готового файла"""
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
    username = "Васян Хмурый"
    payload = {
        "filename": "test-filename",
        "template": template_name,
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        json=payload,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    assert resp.status_code == 201
    resp = await client.get(
        routes.request_to_download_file(filename=data.get("url")),
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    log.debug("", o=data)
    assert resp.status_code == 200
