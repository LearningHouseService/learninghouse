"""The EnforceInitialPasswordChange gate, exercised on its own.

The gate is mounted on a stub application here rather than on the service:
the routes it has to let through include the root redirect, which only
exists when a built UI has been copied into the package - true in a release
build, false in a plain checkout. Testing the middleware directly keeps the
assertion independent of that.
"""

from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from learninghouse.api.middleware import EnforceInitialPasswordChange
from learninghouse.core.settings.models import ServiceSettings
from learninghouse.services.auth import AuthServiceInternal


class StubAuthService:
    def __init__(self, is_initial: bool):
        self.is_initial_admin_password = is_initial


def build_client(is_initial: bool, tmp_path) -> TestClient:
    application = FastAPI()

    for path in ("/", "/ui", "/ui/index.html", "/api/mode", "/api/brain/darkness"):

        @application.get(path)
        async def endpoint():
            return {"reached": True}

    application.add_middleware(
        EnforceInitialPasswordChange,
        settings=ServiceSettings(config_directory=tmp_path),
        auth_service=cast(AuthServiceInternal, StubAuthService(is_initial)),
    )

    return TestClient(application)


class TestWhileTheFallbackPasswordIsInUse:
    @pytest.mark.parametrize("path", ["/", "/ui", "/ui/index.html", "/api/mode"])
    def test_the_allowed_paths_are_reachable(self, path, tmp_path):
        client = build_client(True, tmp_path)

        response = client.get(path, follow_redirects=False)

        assert response.status_code == 200

    def test_everything_else_is_blocked(self, tmp_path):
        client = build_client(True, tmp_path)

        response = client.get("/api/brain/darkness")

        assert response.status_code == 401
        assert response.json()["error"] == "UNAUTHORIZED"


class TestOnceThePasswordIsChanged:
    def test_the_gate_lets_everything_through(self, tmp_path):
        client = build_client(False, tmp_path)

        assert client.get("/api/brain/darkness").status_code == 200
