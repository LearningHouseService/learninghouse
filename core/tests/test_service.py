class TestServiceFixtures:
    def test_client_reaches_versions_endpoint(self, client):
        response = client.get("/api/versions")

        assert response.status_code == 200
        assert "service" in response.json()

    def test_client_uses_the_temporary_config_directory(
        self, client, config_directory, settings
    ):
        assert settings.brains_directory == config_directory.absolute()
