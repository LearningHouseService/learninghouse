"""Pins the predictions the current code produces from a committed, fixed
training dataset - the learninghouse equivalent of the pvlearn baseline (see
docs/modernization-plan.md Phase 2). Phases 5, 7 and 8 change persistence,
feature encoding and the estimator respectively; each of those is measured
against this test. A failure here means predictions changed - regenerate the
pinned values deliberately and say why in the pull request, do not just
update them to make the test pass.

Reproducibility depends on:
- Every row in fixtures/darkness_training_data.csv, and the prediction
  request below, carrying an explicit fixed "timestamp" - add_time_information
  derives month_of_year/day_of_week/hour_of_day/etc. from it and feeds them
  into the model, so a missing timestamp would default to datetime.now() and
  make the result different on every run.
- RandomForestClassifier's random_state=0 and prepare_training's
  train_test_split(random_state=0) (see services/preprocessing.py).
- The exact scikit-learn/pandas/numpy versions pinned in pyproject.toml.

datetime.fromtimestamp() has no explicit timezone (a Phase 7 item, see
docs/modernization-plan.md), so hour_of_day depends on whatever local
timezone the test runs in - the score/features/training_data_size/
prediction assertions below are unaffected (a constant shift across a
timestamped, autocorrelated fixture changes nothing), but the expected
hour_of_day is computed the same way the code does rather than hardcoded,
so the test passes under any timezone rather than only the one it was
written in.
"""

import csv
from datetime import datetime
from pathlib import Path

FIXTURE_FILE = Path(__file__).parent / "fixtures" / "darkness_training_data.csv"

SENSORS = [
    {"name": "azimuth", "typed": "numerical"},
    {"name": "elevation", "typed": "numerical"},
    {"name": "pressure_trend_1h", "typed": "categorical"},
]

BRAIN_CONFIGURATION = {
    "name": "darkness",
    "estimator": {
        "typed": "classifier",
        "estimators": 100,
        "max_depth": 5,
        "random_state": 0,
    },
    "dependent_encode": True,
    "test_size": 0.2,
}


def _load_fixture_rows() -> list[dict]:
    with open(FIXTURE_FILE, newline="", encoding="utf-8") as fixture_file:
        return list(csv.DictReader(fixture_file))


def _train_baseline_brain(client, headers) -> dict:
    for sensor in SENSORS:
        response = client.post(
            "/api/sensor/configuration", json=sensor, headers=headers
        )
        assert response.status_code == 201, response.json()

    response = client.post(
        "/api/brain/configuration", json=BRAIN_CONFIGURATION, headers=headers
    )
    assert response.status_code == 201, response.json()

    last_response = None
    for row in _load_fixture_rows():
        last_response = client.put(
            "/api/brain/darkness/training",
            json={
                "dependent_value": row["darkness"] == "true",
                "sensors_data": {
                    "timestamp": int(row["timestamp"]),
                    "azimuth": float(row["azimuth"]),
                    "elevation": float(row["elevation"]),
                    "pressure_trend_1h": row["pressure_trend_1h"],
                },
            },
            headers=headers,
        )

    assert last_response is not None
    assert last_response.status_code == 200, last_response.json()
    return last_response.json()


class TestBaseline:
    def test_training_on_the_fixture_dataset_is_pinned(
        self, isolated_client, unlocked_admin_headers
    ):
        info = _train_baseline_brain(isolated_client, unlocked_admin_headers)

        assert info["training_data_size"] == 20
        assert info["score"] == 1.0
        assert sorted(info["features"]) == ["azimuth", "elevation", "hour_of_day"]

    def test_prediction_on_a_fixed_input_is_pinned(
        self, isolated_client, unlocked_admin_headers
    ):
        _train_baseline_brain(isolated_client, unlocked_admin_headers)

        prediction_timestamp = 1700072000
        response = isolated_client.post(
            "/api/brain/darkness/prediction",
            json={
                "timestamp": prediction_timestamp,
                "azimuth": 200.0,
                "elevation": -5.0,
                "pressure_trend_1h": "falling",
            },
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] is True
        expected_hour = float(datetime.fromtimestamp(prediction_timestamp).hour)
        assert body["preprocessed"] == {
            "azimuth": 200.0,
            "elevation": -5.0,
            "hour_of_day": expected_hour,
        }
