"""Characterization tests for learninghouse.api.sensor."""

from tests.conftest import unlock

SENSOR = {"name": "azimuth", "typed": "numerical"}


def _create_sensor(client, headers, sensor: dict = SENSOR) -> None:
    response = client.post("/api/sensor/configuration", json=sensor, headers=headers)
    assert response.status_code == 201, response.json()


class TestGetSensorsConfiguration:
    def test_lists_all_configured_sensors(
        self, isolated_client, unlocked_admin_headers
    ):
        _create_sensor(isolated_client, unlocked_admin_headers)

        response = isolated_client.get(
            "/api/sensors/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        names = [sensor["name"] for sensor in response.json()]
        assert names == ["azimuth"]

    def test_missing_credentials_are_rejected(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.get("/api/sensors/configuration")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestGetSensorConfiguration:
    def test_existing_sensor_is_returned(self, isolated_client, unlocked_admin_headers):
        _create_sensor(isolated_client, unlocked_admin_headers)

        response = isolated_client.get(
            "/api/sensor/azimuth/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json() == {
            "name": "azimuth",
            "typed": "numerical",
            "cycles": 0,
            "calc_sun_position": False,
        }

    def test_unknown_sensor_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.get(
            "/api/sensor/does-not-exist/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_SENSOR"


class TestPostSensorConfiguration:
    def test_creates_a_new_sensor(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.post(
            "/api/sensor/configuration", json=SENSOR, headers=unlocked_admin_headers
        )

        assert response.status_code == 201
        assert response.json()["name"] == "azimuth"

    def test_duplicate_name_is_rejected(self, isolated_client, unlocked_admin_headers):
        _create_sensor(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/sensor/configuration", json=SENSOR, headers=unlocked_admin_headers
        )

        assert response.status_code == 400
        assert response.json()["error"] == "EXISTS"


class TestPutSensorConfiguration:
    def test_updates_an_existing_sensor(self, isolated_client, unlocked_admin_headers):
        _create_sensor(isolated_client, unlocked_admin_headers)

        response = isolated_client.put(
            "/api/sensor/azimuth/configuration",
            json={"name": "azimuth", "typed": "cyclical", "cycles": 360},
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["typed"] == "cyclical"
        assert body["cycles"] == 360

    def test_unknown_sensor_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.put(
            "/api/sensor/does-not-exist/configuration",
            json=SENSOR,
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_SENSOR"


class TestDeleteSensorConfiguration:
    def test_deletes_an_existing_sensor(self, isolated_client, unlocked_admin_headers):
        _create_sensor(isolated_client, unlocked_admin_headers)

        response = isolated_client.delete(
            "/api/sensor/azimuth/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json()["name"] == "azimuth"

        listed = isolated_client.get(
            "/api/sensors/configuration", headers=unlocked_admin_headers
        )
        assert listed.json() == []

    def test_unknown_sensor_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.delete(
            "/api/sensor/does-not-exist/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_SENSOR"
