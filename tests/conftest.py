import asyncio
from datetime import timedelta
from typing import AsyncGenerator
from typing import Generator

import pytest
from _pytest.config import ExitCode

from _pytest.main import Session
from _pytest.nodes import Item
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import URL

from logrich.logger_ import log  # noqa

from logrich.logger_assets import console

from src.docx.config import config

from src.docx.helpers.security import generate_jwt
from src.docx.main import run_app as app_
from repo.repo_assets import get_test_status_badge
from tests.test_tools import print_request, print_endpoints
from httpx import AsyncClient, Headers


def pytest_sessionfinish(session: Session, exitstatus: int | ExitCode) -> None:
    """получит бейдж для статуса тестов"""
    print()
    if config.LOCAL:
        # log.debug(config.LOCAL)
        asyncio.run(get_test_status_badge(status=exitstatus))


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir: str) -> Generator:
    """Fixture to execute asserts before and after a test is run"""
    print()
    yield


@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    yield app_()


def pytest_sessionstart(session: Session) -> None:  # noqa
    """"""
    if not config.TESTING:
        log.warning("включите режим тестирования - установите переменную TESTING=1")
        pytest.exit("-")


def pytest_runtest_call(item: Item) -> None:
    """печатает заголовок теста"""
    console.rule(f"[green]{item.parent.name}[/]::[yellow bold]{item.name}[/]")  # type: ignore


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, object]:
    """Async server client that handles lifespan and teardown"""
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://test",
            event_hooks={
                "request": [print_request],
            },
        ) as client_:
            try:
                yield client_
            except Exception as exc:
                log.error(exc)
            finally:
                pass


async def auth_headers(
    audience: str,
    lifetime: timedelta = timedelta(days=1),
    token_issuer: str = "test-auth.site.com",
    namespace: str | None = None,
) -> Headers:
    """Returns the authorization headers"""

    token_data = {"iss": token_issuer, "aud": audience, "nsp": namespace}

    token = generate_jwt(data=token_data, lifetime=lifetime)
    # log.debug(token)
    return Headers({"AUTHORIZATION": "Bearer " + token})


class Routs:
    def __init__(self, app: FastAPI) -> None:
        # Request for create docx
        self.app = app
        self.request_to_create_docx = app.url_path_for("create_docx")
        self.request_to_upload_template = app.url_path_for("upload_template")
        self.request_to_list_templates = app.url_path_for("list_templates")

    def request_to_download_template(self, filename: str) -> URL | str:
        return self.app.url_path_for("download_template", filename=str(filename))

    def request_to_download_file(self, filename: str) -> URL | str:
        return self.app.url_path_for("download_file", filename=str(filename))

    def print(self) -> None:
        print_endpoints(self.app)


@pytest.fixture
def routes(app: FastAPI) -> Routs:
    """ """
    return Routs(app)
