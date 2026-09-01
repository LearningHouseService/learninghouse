"""The application built by `learninghouse.service.get_application`, plus
the fixtures the rest of the suite builds on.
"""


class TestServiceFixtures:
    def test_client_reaches_versions_endpoint(self, client):
        response = client.get("/api/versions")

        assert response.status_code == 200
        assert "service" in response.json()

    def test_client_uses_the_temporary_config_directory(
        self, client, config_directory, settings
    ):
        assert settings.brains_directory == config_directory.absolute()


class TestCors:
    """`allow_origins=["*"]` next to `allow_credentials=True` was replaced
    with a configurable list. Starlette answers that combination by
    reflecting the request's own Origin header, so before this change every
    page a user visited could call their instance with their session.
    """

    def test_an_unconfigured_origin_gets_no_allow_origin_header(
        self, configured_client
    ):
        client = configured_client()

        response = client.get(
            "/api/versions", headers={"Origin": "https://evil.example"}
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers

    def test_a_credentialed_preflight_from_an_unconfigured_origin_is_rejected(
        self, configured_client
    ):
        client = configured_client()

        response = client.options(
            "/api/auth/token",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization",
            },
        )

        assert response.status_code == 400
        assert "access-control-allow-origin" not in response.headers

    def test_a_configured_origin_is_allowed_with_credentials(self, configured_client):
        client = configured_client(cors_allowed_origins=["https://home.example"])

        response = client.get(
            "/api/versions", headers={"Origin": "https://home.example"}
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "https://home.example"
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_the_default_origin_is_the_services_own(self, configured_client):
        # Nothing configured: the UI is served from the service's own origin,
        # so that is the one origin that keeps working out of the box.
        client = configured_client()

        response = client.get(
            "/api/versions", headers={"Origin": "http://localhost:5000"}
        )

        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:5000"
        )
