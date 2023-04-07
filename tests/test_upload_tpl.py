import pathlib

import pytest
from docxtpl import DocxTemplate
from src.docx.config import config

from logrich.logger_ import log  # noqa
from httpx import AsyncClient, Headers
from src.docx.helpers.tools import duration  # noqa
from tests.conftest import Routs, auth_headers

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test_nsp")])
async def test_upload_tpl(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона"""
    # config.FILE_MAX_SIZE = 0.001
    headers: Headers = await auth_headers(audience=audience, namespace=namespace)
    # log.debug(headers)
    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.docx"
    file = ("file", open(path_to_file, "rb"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера.."
    out_file = pathlib.Path(
        f'{config.TEMPLATES_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("template")}'
    )

    assert out_file.is_file(), "Шаблон не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert "Здравствуй мир!" in " ".join(
        content
    ), "Содержимое исходного шаблона и загруженного не соответствует."
    # зачистим артефакты
    pathlib.Path(out_file).unlink()


# @duration
# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test_nsp")])
async def test_upload_tpl_with_fake_jwt(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона с неправильным токеном"""
    # config.FILE_MAX_SIZE = 0.001

    payload = {"filename": "temp_dir/test-filename.docx", "replace_if_exist": True}
    path_to_file = "tests/files/test_docx_template_to_upload.txt"
    file = ("file", open(path_to_file, "rb"))
    header = await auth_headers(audience=audience, namespace=namespace)
    # log.debug(header.get("authorization"))
    # header.update({"authorization": "fake_fake_fake"})
    header.update({"authorization": "Bearer fake_fake_fake"})
    # log.debug(header.get("authorization"))
    resp = await client.put(
        routes.request_to_upload_template,
        files=[file],
        data=payload,
        headers=header,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 403, "некорректный ответ сервера.."


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-super"], "test_nsp")])
async def test_upload_tpl_with_super_aud(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона с аудиенцией super"""

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
    log.debug("--", o=data)
    # return
    assert resp.status_code == 201, "некорректный ответ сервера.."
    out_file = pathlib.Path(
        f'{config.TEMPLATES_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("template")}'
    )

    assert out_file.is_file(), "Шаблон не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert "Здравствуй мир!" in " ".join(
        content
    ), "Содержимое исходного шаблона и загруженного не соответствует."

    # зачистим артефакты
    out_file.unlink()


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize("audience,namespace", [(["other-aud", "docx-update"], "test_nsp")])
async def test_upload_tpl_without_filename(
    client: AsyncClient, routes: Routs, audience: str, namespace: str
) -> None:
    """тест загрузки шаблона без указания имени"""

    payload = {"replace_if_exist": True}
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
    out_file = pathlib.Path(
        f'{config.TEMPLATES_DIR}/{data.get("issuer")}/{data.get("nsp")}/{data.get("template")}'
    )

    assert out_file.is_file(), "Шаблон не сохранился"

    doc = DocxTemplate(str(out_file))
    doc.render({})
    content = set()
    for para in doc.paragraphs:
        content.add(para.text)
    assert "Здравствуй мир!" in " ".join(
        content
    ), "Содержимое исходного шаблона и загруженного не соответствует."

    # зачистим артефакты
    out_file.unlink()
