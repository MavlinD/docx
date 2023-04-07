import pathlib

import pytest
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa

from src.docx.config import config
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["other-aud", "docx-create", "docx-delete", "docx-update"], "test-nsp")]
)
async def test_delete_tpl(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест удаления шаблона"""
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    # сначала загрузим шаблон
    headers: Headers = await auth_headers(audience=audience, namespace=namespace)
    # log.debug(headers)
    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": str(True)}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=headers,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    check_file = pathlib.Path(
        f'{config.TEMPLATES_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("template")}'
    )
    assert resp.status_code == 201, "некорректный ответ сервера.."
    out_file = pathlib.Path(data.get("template"))
    # log.debug(out_file)
    assert check_file.is_file(), "файл не загрузился"
    # return
    # теперь удалим
    resp = await client.delete(
        routes.request_to_delete_file(filename=out_file),
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    check_file = pathlib.Path(
        f'{config.TEMPLATES_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("template")}'
    )
    assert resp.status_code == 202, "некорректный ответ сервера"
    assert not check_file.is_file(), "файл не удалился"
