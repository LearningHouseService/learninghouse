"""Shared pytest fixtures for the characterization suite.

`service_settings()` and `authservice` are process-global singletons until
Phase 2's de-globalization work lands (see docs/modernization-plan.md). That
means every worker process gets exactly one brains directory for its whole
session: the environment variable below must be set before the first
`learninghouse` import happens anywhere, which is why it runs from
`pytest_configure` rather than a fixture, and why nothing in this module
imports `learninghouse` at module level.

Under `pytest-xdist` (`-n auto` in pyproject.toml) each worker is a separate
process with its own `pytest_configure` call, so workers do not share a
directory with each other - only tests within the same worker do.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

    from learninghouse.core.settings.models import ServiceSettings

_CONFIG_DIRECTORY_ENV = "LEARNINGHOUSE_CONFIG_DIRECTORY"

DEFAULT_ADMIN_PASSWORD = "learninghouse"
UNLOCKED_ADMIN_PASSWORD = "unlocked-test-password-1"


def pytest_configure(config: pytest.Config) -> None:
    # pylint: disable=unused-argument
    config_directory = Path(tempfile.mkdtemp(prefix="learninghouse-tests-"))
    os.environ[_CONFIG_DIRECTORY_ENV] = str(config_directory)


def pytest_unconfigure(config: pytest.Config) -> None:
    # pylint: disable=unused-argument
    config_directory = os.environ.pop(_CONFIG_DIRECTORY_ENV, None)
    if config_directory:
        shutil.rmtree(config_directory, ignore_errors=True)


@pytest.fixture(scope="session")
def config_directory() -> Path:
    return Path(os.environ[_CONFIG_DIRECTORY_ENV])


@pytest.fixture(scope="session")
def settings() -> "ServiceSettings":
    from learninghouse.core.settings import service_settings

    return service_settings()


@pytest.fixture(scope="session")
def client() -> Iterator["TestClient"]:
    from fastapi.testclient import TestClient

    from learninghouse.service import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def isolated_client() -> Iterator["TestClient"]:
    """A fresh brains directory, settings and auth service for a single test.

    `service_settings()` and `auth_service_cached()` are both process-wide
    `lru_cache`s with no parameters (see docs/modernization-plan.md Phase 2).
    The session-scoped `client` fixture above is stuck with whichever
    directory `pytest_configure` picked for the whole worker - fine for
    read-only smoke tests, but not for anything that logs in, changes the
    admin password, or otherwise mutates the security database, since that
    would leak into every other test sharing the same worker.

    This fixture points the config directory env var at a brand new
    directory, clears both caches so the next resolution picks it up, builds
    a fresh app from it, and restores everything on teardown. Tests using
    this fixture always see the initial admin password ("learninghouse") and
    an empty security database, independent of any other test in the same
    session - this is what makes "two tests in the same session use two
    different brains directories" true in practice, not just in principle.
    """
    from fastapi.testclient import TestClient

    from learninghouse.core.settings import service_settings
    from learninghouse.service import get_application
    from learninghouse.services.auth import auth_service_cached

    config_directory = Path(tempfile.mkdtemp(prefix="learninghouse-tests-"))
    previous_config_directory = os.environ.get(_CONFIG_DIRECTORY_ENV)
    os.environ[_CONFIG_DIRECTORY_ENV] = str(config_directory)
    service_settings.cache_clear()
    auth_service_cached.cache_clear()

    try:
        with TestClient(get_application()) as test_client:
            yield test_client
    finally:
        if previous_config_directory is None:
            os.environ.pop(_CONFIG_DIRECTORY_ENV, None)
        else:
            os.environ[_CONFIG_DIRECTORY_ENV] = previous_config_directory
        service_settings.cache_clear()
        auth_service_cached.cache_clear()
        shutil.rmtree(config_directory, ignore_errors=True)


def login(client, password: str = DEFAULT_ADMIN_PASSWORD) -> dict:
    response = client.post("/api/auth/token", json={"password": password})
    assert response.status_code == 200
    return response.json()


def admin_headers(client, password: str = DEFAULT_ADMIN_PASSWORD) -> dict:
    token = login(client, password)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def unlock(client, new_password: str = UNLOCKED_ADMIN_PASSWORD) -> None:
    """Change the admin password away from its initial fallback value.

    EnforceInitialPasswordChange blocks every endpoint that is not on its
    allow-list ("/api/auth/token", "/api/auth/password", "/api/mode",
    "/api/versions", static/ui/docs) for as long as the admin password is
    still the fallback one - regardless of whether the request's own
    credentials would otherwise be valid. Any test exercising a brain,
    sensor, or non-token/password auth endpoint needs this as setup first,
    or it ends up characterizing this gate instead of the endpoint itself.
    """
    headers = admin_headers(client)
    response = client.put(
        "/api/auth/password",
        json={"old_password": DEFAULT_ADMIN_PASSWORD, "new_password": new_password},
        headers=headers,
    )
    assert response.status_code == 200


@pytest.fixture()
def unlocked_client(isolated_client: "TestClient") -> "TestClient":
    unlock(isolated_client)
    return isolated_client


@pytest.fixture()
def unlocked_admin_headers(unlocked_client: "TestClient") -> dict:
    return admin_headers(unlocked_client, UNLOCKED_ADMIN_PASSWORD)
