import pytest
from httpx import AsyncClient

from datetime import timedelta
from logrich.logger_ import log  # noqa

from src.docx.helpers.tools import sanity_str
from tests.conftest import Routs, auth_headers
from pathvalidate import sanitize_filepath
from transliterate import translit

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-create"], "test-nsp")])
async def test_expire_token(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест невозможности создания docx с просроченным токеном
    https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-document
    """
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        headers=await auth_headers(
            audience=audience, lifetime=timedelta(days=-1), namespace=namespace
        ),
        json=payload,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    assert resp.status_code == 403, "некорректный ответ сервера"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "audience,namespace", [(["other-aud", "docx-create"], "test-nsp,second-nsp")]
)
async def test_token_with_only_one_nsp(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест невозможности создания docx с токеном в котором более одного неймспейса"""
    username = "Васян Хмурый"
    # log.debug(token)
    payload = {
        "filename": "test-filename",
        "template": "test_docx_template.docx",
        "context": {"username": username, "place": "Кемерово"},
    }
    resp = await client.post(
        routes.request_to_create_docx,
        headers=await auth_headers(audience=audience, namespace=namespace),
        json=payload,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    assert resp.status_code == 400, "некорректный ответ сервера"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_sinitaze_file_path() -> None:
    """тест транслитерации файловых путей"""
    filename: str = "Мой за#мечате@льный шабл%он.xlsm"
    new_name = sanity_str(string=filename)
    log.debug(new_name)
    assert new_name == "moj_zamechatelnyj_shablon.xlsm"
