"""Characterization tests for learninghouse.api.brain.

Training needs sensors configured first (DatasetPreprocessing.sensorsconfig
reads sensors.json) and at least 10 pushed data points before the service
actually trains anything - see BrainService.request/train. The helpers below
set up a minimal "darkness" brain: two numerical sensors, one categorical,
and a boolean dependent value that correlates with elevation so the
estimator has a real signal to find. This is throwaway fixture data for
exercising the endpoints, not the pinned baseline dataset from Task 9.
"""

from tests.conftest import unlock

BRAIN_NAME = "darkness"

SENSORS = [
    {"name": "azimuth", "typed": "numerical"},
    {"name": "elevation", "typed": "numerical"},
    {"name": "pressure_trend_1h", "typed": "categorical"},
]

BRAIN_CONFIGURATION = {
    "name": BRAIN_NAME,
    "estimator": {
        "typed": "classifier",
        "estimators": 100,
        "max_depth": 5,
        "random_state": 0,
    },
    "dependent_encode": True,
    "test_size": 0.2,
}


def _create_sensors(client, headers) -> None:
    for sensor in SENSORS:
        response = client.post(
            "/api/sensor/configuration", json=sensor, headers=headers
        )
        assert response.status_code == 201, response.json()


def _create_brain_configuration(client, headers, name: str = BRAIN_NAME) -> dict:
    configuration = {**BRAIN_CONFIGURATION, "name": name}
    response = client.post(
        "/api/brain/configuration", json=configuration, headers=headers
    )
    assert response.status_code == 201, response.json()
    return configuration


def _training_row(index: int) -> tuple[dict, bool]:
    elevation = -30 + index * 5
    sensors_data = {
        "azimuth": 100 + index * 10,
        "elevation": elevation,
        "pressure_trend_1h": "rising" if index % 2 == 0 else "falling",
    }
    return sensors_data, elevation <= 0


def _push_training_rows(client, headers, name: str = BRAIN_NAME, rows: int = 10):
    last_response = None
    for index in range(rows):
        sensors_data, dependent_value = _training_row(index)
        last_response = client.put(
            f"/api/brain/{name}/training",
            json={"dependent_value": dependent_value, "sensors_data": sensors_data},
            headers=headers,
        )
    return last_response


def _set_up_trained_brain(client, headers, name: str = BRAIN_NAME) -> None:
    _create_sensors(client, headers)
    _create_brain_configuration(client, headers, name)
    response = _push_training_rows(client, headers, name, rows=10)
    assert response is not None
    assert response.status_code == 200, response.json()


class TestInfosGet:
    def test_lists_all_brains(self, isolated_client, unlocked_admin_headers):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.get(
            "/api/brains/info", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert BRAIN_NAME in response.json()

    def test_missing_credentials_are_rejected(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.get("/api/brains/info")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestInfoGet:
    def test_configured_but_untrained_brain_reports_zero_score(
        self, isolated_client, unlocked_admin_headers
    ):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.get(
            f"/api/brain/{BRAIN_NAME}/info", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["score"] == 0.0
        assert body["trained_at"] is None

    def test_unknown_brain_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.get(
            "/api/brain/does-not-exist/info", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_CONFIGURATION"


class TestTrainingPost:
    def test_retrains_from_existing_data(self, isolated_client, unlocked_admin_headers):
        _set_up_trained_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            f"/api/brain/{BRAIN_NAME}/training", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json()["trained_at"] is not None

    def test_brain_with_no_training_data_yet_is_rejected(
        self, isolated_client, unlocked_admin_headers
    ):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            f"/api/brain/{BRAIN_NAME}/training", headers=unlocked_admin_headers
        )

        assert response.status_code == 202
        assert response.json()["error"] == "NOT_ENOUGH_TRAINING_DATA"


class TestTrainingPut:
    def test_first_nine_rows_are_saved_but_not_yet_trained(
        self, isolated_client, unlocked_admin_headers
    ):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = _push_training_rows(isolated_client, unlocked_admin_headers, rows=9)

        assert response is not None
        assert response.status_code == 202
        assert response.json()["error"] == "NOT_ENOUGH_TRAINING_DATA"

    def test_tenth_row_trains_the_brain(self, isolated_client, unlocked_admin_headers):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = _push_training_rows(isolated_client, unlocked_admin_headers, rows=10)

        assert response is not None
        assert response.status_code == 200
        body = response.json()
        assert body["training_data_size"] == 10
        assert body["trained_at"] is not None


class TestPredictionPost:
    def test_trained_brain_returns_a_prediction(
        self, isolated_client, unlocked_admin_headers
    ):
        _set_up_trained_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            f"/api/brain/{BRAIN_NAME}/prediction",
            json={"azimuth": 150, "elevation": -10, "pressure_trend_1h": "falling"},
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body["prediction"], bool)
        assert body["brain"]["name"] == BRAIN_NAME

    def test_untrained_brain_is_rejected(self, isolated_client, unlocked_admin_headers):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            f"/api/brain/{BRAIN_NAME}/prediction",
            json={"azimuth": 150, "elevation": -10, "pressure_trend_1h": "falling"},
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NOT_TRAINED"

    def test_brain_trained_under_different_library_versions_is_rejected(
        self, isolated_client, unlocked_admin_headers, monkeypatch
    ):
        """Guards Brain.actual_versions (models/brain.py), the check Phase 3's
        scikit-learn bump relies on: a brain trained under one library set
        must be rejected, not silently loaded, once the running versions
        differ - see docs/modernization-plan.md Phase 3.

        Training happens first with the real `versions`, so the pickled
        Brain.versions snapshot captures it; the running versions.sklearn is
        then changed post-training to simulate an upgrade that happened after
        training, without needing to actually install a different
        scikit-learn build to prove the check works.
        """
        _set_up_trained_brain(isolated_client, unlocked_admin_headers)

        import learninghouse.models.brain as brain_module

        upgraded_versions = brain_module.versions.model_copy(
            update={"sklearn": "0.0.0-test-upgrade"}
        )
        monkeypatch.setattr(brain_module, "versions", upgraded_versions)

        response = isolated_client.post(
            f"/api/brain/{BRAIN_NAME}/prediction",
            json={"azimuth": 150, "elevation": -10, "pressure_trend_1h": "falling"},
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 428
        assert response.json()["error"] == "NOT_ACTUAL"


class TestConfigurationGet:
    def test_existing_brain_configuration_is_returned(
        self, isolated_client, unlocked_admin_headers
    ):
        _create_sensors(isolated_client, unlocked_admin_headers)
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.get(
            f"/api/brain/{BRAIN_NAME}/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json()["name"] == BRAIN_NAME

    def test_unknown_brain_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.get(
            "/api/brain/does-not-exist/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_CONFIGURATION"


class TestConfigurationPost:
    def test_creates_a_new_brain(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.post(
            "/api/brain/configuration",
            json=BRAIN_CONFIGURATION,
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 201
        assert response.json()["name"] == BRAIN_NAME

    def test_duplicate_name_is_rejected(self, isolated_client, unlocked_admin_headers):
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/brain/configuration",
            json=BRAIN_CONFIGURATION,
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 400
        assert response.json()["error"] == "EXISTS"


class TestConfigurationPut:
    def test_updates_an_existing_brain(self, isolated_client, unlocked_admin_headers):
        _create_brain_configuration(isolated_client, unlocked_admin_headers)
        updated = {**BRAIN_CONFIGURATION, "test_size": 0.3}

        response = isolated_client.put(
            f"/api/brain/{BRAIN_NAME}/configuration",
            json=updated,
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["test_size"] == 0.3

    def test_unknown_brain_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.put(
            "/api/brain/does-not-exist/configuration",
            json=BRAIN_CONFIGURATION,
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_CONFIGURATION"


class TestConfigurationDelete:
    def test_deletes_an_existing_brain(self, isolated_client, unlocked_admin_headers):
        _create_brain_configuration(isolated_client, unlocked_admin_headers)

        response = isolated_client.delete(
            f"/api/brain/{BRAIN_NAME}/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json()["name"] == BRAIN_NAME

        listed = isolated_client.get("/api/brains/info", headers=unlocked_admin_headers)
        assert BRAIN_NAME not in listed.json()

    def test_unknown_brain_is_rejected(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.delete(
            "/api/brain/does-not-exist/configuration", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_CONFIGURATION"
