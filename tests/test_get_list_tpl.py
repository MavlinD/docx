import pathlib

# from collections import Mapping
from collections import namedtuple
from types import MappingProxyType
from typing import Mapping, Sequence

import pytest
from docxtpl import DocxTemplate
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa

from src.docx.config import config
from src.docx.helpers.security import generate_jwt
from tests.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_list_tpl(client: AsyncClient, routes: Routs, auth_headers: Headers) -> None:
    """тест на получение списка шаблонов"""

    # log.debug(list(config.content_type_white_list.keys()))
    # return
    # token_issuer = "test-auth.site.com"
    # token_data = {
    #     "iss": token_issuer,
    #     "aud": ["other-aud", "docx-create"],
    # }
    # token = generate_jwt(data=token_data)
    # log.debug(token)
    # payload = {"token": token}
    resp = await client.get(
        routes.request_to_list_templates,
        headers=auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    return
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
