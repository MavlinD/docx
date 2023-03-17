import json
import pathlib

# from collections import Mapping
from collections import namedtuple
from types import MappingProxyType
from typing import Mapping, Sequence

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient

from logrich.logger_ import log  # noqa

from src.docx.config import config
from src.docx.helpers.security import generate_jwt
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-update"])])
async def test_upload_tpl(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест загрузки шаблона"""
    # config.FILE_MAX_SIZE = 0.001

    # log.debug(list(config.content_type_white_list.keys()))
    # return
    # token_issuer = "test-auth.site.com"
    # token_data = {
    #     "iss": token_issuer,
    #     "aud": ["other-aud", "docx-update"],
    # }
    # token = generate_jwt(data=token_data)
    # log.debug(token)
    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    # path_to_file = "tests/files/nginx.png"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера.."
    out_file = pathlib.Path(data.get("template"))

    assert out_file.is_file(), "Шаблон не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert "Здравствуй мир!" in " ".join(
        content
    ), "Содержимое исходного шаблона и загруженного не соответствует."
