import pytest
from httpx import AsyncClient, Headers

from logrich.logger_ import log  # noqa

from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience", [(["other-aud", "docx-read"])])
async def test_get_list_tpl(client: AsyncClient, routes: Routs, audience: str) -> None:
    """тест на получение списка шаблонов"""

    resp = await client.get(
        routes.request_to_list_templates,
        headers=await auth_headers(audience=audience),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert resp.status_code == 200, "некорректный ответ сервера."
    assert isinstance(data, list)
