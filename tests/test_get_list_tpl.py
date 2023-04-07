from pathlib import Path

import pytest
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from src.docx.config import config
from src.docx.schemas import JWT
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["other-aud", "docx-read", "docx-update"], "test-nsp")]
)
async def test_get_list_tpl(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест на получение списка шаблонов"""
    headers = await auth_headers(audience=audience, namespace=namespace)
    # определим издателя токена
    token = JWT(
        token=headers.get("Authorization")[7:].strip(), path_to_authorized_keys="authorized_keys"
    )
    token.set_issuer()
    token.audience = audience
    jwt_payload = await token.decode_jwt
    # log.debug("", o=jwt_payload)
    # return
    # сначала удалим все ранее загруженные шаблоны
    for p in Path(f"{config.TEMPLATES_DIR}/{token.issuer}/{token.nsp}").glob("**/*.docx"):
        # log.trace(p)
        p.unlink()

    # поместим пару шаблонов
    payload = {"filename": "test-filename.docx", "replace_if_exist": True}
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
    # return
    assert resp.status_code == 201, "некорректный ответ сервера."

    payload2 = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload2,
        headers=await auth_headers(audience=audience, namespace=namespace),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера."
    # получим список шаблонов
    resp = await client.get(
        routes.request_to_list_templates,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 200, "некорректный ответ сервера."
    assert isinstance(data.get("templates"), list)
    assert data.get("issuer") == token.issuer
    assert data.get("templates") == [
        payload["filename"],
        payload2["filename"],
    ]
