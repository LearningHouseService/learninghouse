"""Characterization tests for the service-tagged routes declared directly in
learninghouse.api (__init__.py): GET /api/mode and GET /api/versions.
"""

from tests.conftest import unlock


class TestGetMode:
    def test_reports_initial_while_password_is_the_fallback(self, isolated_client):
        response = isolated_client.get("/api/mode")

        assert response.status_code == 200
        assert response.json() == "initial"

    def test_reports_the_environment_after_password_change(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.get("/api/mode")

        assert response.status_code == 200
        assert response.json() == "production"


class TestGetVersions:
    def test_reports_service_and_library_versions(self, isolated_client):
        response = isolated_client.get("/api/versions")

        assert response.status_code == 200
        body = response.json()
        assert body["service"]
        for library in (
            "fastapi",
            "pydantic",
            "uvicorn",
            "sklearn",
            "numpy",
            "pandas",
            "jwt",
            "argon2",
            "loguru",
        ):
            assert body[library]

    def test_is_reachable_without_credentials(self, isolated_client):
        # /api/versions is on EnforceInitialPasswordChange's allow-list and
        # carries no auth dependency of its own.
        response = isolated_client.get("/api/versions")

        assert response.status_code == 200
