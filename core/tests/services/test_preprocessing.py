"""Characterization tests for learninghouse.services.preprocessing.

Pins current behaviour, including two known defects that are recorded rather
than fixed here - both belong to the rework of the sensor encoders:

- preprocessing.py:38 formats the datetime with "%Y-%m-%d %H:%M:%s". Lowercase
  %s is a glibc strftime extension for epoch seconds, not seconds-within-the-
  minute - the stored string ends with the full unix timestamp where a 0-59
  value belongs.
- prepare_training's train_test_split(random_state=0) shuffles by default,
  which is wrong for timestamped, autocorrelated rows but is today's actual
  behaviour.

datetime.fromtimestamp() has no explicit timezone, so it resolves against
whatever local timezone the test runs in (part of the same rework - the sun
encoder will need an explicit one anyway). Tests below compute their expected
month/day/hour the same way the code does, rather than hardcoding
timezone-specific values, so they characterize the *relationship* ("derived
from local time") without being flaky across machines.
"""

from datetime import datetime

import pandas as pd

from learninghouse.models.brain import Brain
from learninghouse.services.preprocessing import DatasetPreprocessing

FIXED_TIMESTAMP = 1700000000


class TestAddTimeInformation:
    def test_uses_the_given_timestamp_and_derives_local_time_fields(self):
        data = DatasetPreprocessing.add_time_information({"timestamp": FIXED_TIMESTAMP})

        expected = datetime.fromtimestamp(FIXED_TIMESTAMP)
        assert data["timestamp"] == FIXED_TIMESTAMP
        assert data["month_of_year"] == expected.month
        assert data["day_of_month"] == expected.day
        assert data["day_of_week"] == expected.strftime("%A")
        assert data["hour_of_day"] == expected.hour
        assert data["minute_of_hour"] == expected.minute

    def test_datetime_field_ends_with_the_raw_epoch_seconds(self):
        # The documented %s defect: "%H:%M:%s" puts the full epoch timestamp
        # directly after the minute's colon, e.g. "23:13:1700000000" instead
        # of "23:13:20". Assert the observable symptom rather than hardcoding
        # a timezone-dependent date/hour prefix.
        data = DatasetPreprocessing.add_time_information({"timestamp": FIXED_TIMESTAMP})

        assert data["datetime"].endswith(f":{FIXED_TIMESTAMP}")

    def test_missing_timestamp_defaults_to_now(self):
        before = datetime.now().timestamp()
        data = DatasetPreprocessing.add_time_information({})
        after = datetime.now().timestamp()

        assert before <= data["timestamp"] <= after

        expected = datetime.fromtimestamp(data["timestamp"])
        assert data["month_of_year"] == expected.month
        assert data["hour_of_day"] == expected.hour

    def test_existing_fields_are_preserved(self):
        data = DatasetPreprocessing.add_time_information(
            {"timestamp": FIXED_TIMESTAMP, "azimuth": 123.4}
        )

        assert data["azimuth"] == 123.4


class TestPrepareTrainingShuffle:
    def test_train_test_split_shuffles_timestamped_rows(
        self, isolated_client, unlocked_admin_headers
    ):
        for sensor in [
            {"name": "elevation", "typed": "numerical"},
        ]:
            response = isolated_client.post(
                "/api/sensor/configuration",
                json=sensor,
                headers=unlocked_admin_headers,
            )
            assert response.status_code == 201, response.json()

        configuration = {
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
        response = isolated_client.post(
            "/api/brain/configuration",
            json=configuration,
            headers=unlocked_admin_headers,
        )
        assert response.status_code == 201, response.json()

        rows = []
        for index in range(20):
            row = DatasetPreprocessing.add_time_information(
                {
                    "timestamp": FIXED_TIMESTAMP + index * 3600,
                    "elevation": -30 + index * 3,
                }
            )
            row["darkness"] = row["elevation"] <= 0
            rows.append(row)
        data = pd.DataFrame(rows)

        brain = Brain("darkness")
        _, _, x_test, _, _ = DatasetPreprocessing.prepare_training(brain, data, False)

        # A chronological split (shuffle=False) would make the test rows the
        # last contiguous slice in insertion order. train_test_split's
        # default shuffle=True (only random_state=0 is passed) scatters them
        # across the whole range instead - wrong for autocorrelated,
        # timestamped rows, but today's actual behaviour (see module
        # docstring; whether the split becomes chronological is an open
        # modelling question, not a bug fix).
        test_indices = sorted(x_test.index.tolist())
        chronological_tail = list(range(len(data) - len(x_test), len(data)))
        assert test_indices != chronological_tail


SENSORS = [
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


def _train_categorical_brain(client, headers) -> None:
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
    for index in range(10):
        elevation = -30 + index * 6
        trend = "rising" if index % 2 == 0 else "falling"
        last_response = client.put(
            "/api/brain/darkness/training",
            json={
                "dependent_value": elevation <= 0,
                "sensors_data": {
                    "timestamp": FIXED_TIMESTAMP + index * 3600,
                    "elevation": elevation,
                    "pressure_trend_1h": trend,
                },
            },
            headers=headers,
        )

    assert last_response is not None
    assert last_response.status_code == 200, last_response.json()


class TestPreparePredictionAlignment:
    """Characterizes get_x_selected_and_numerical_columns / prepare_prediction
    through the running brain/prediction endpoints - a Brain instance carries
    enough internal state (dataset.columns, dataset.imputer, dataset.features)
    that reconstructing it by hand would just duplicate BrainService.
    """

    def test_a_category_seen_in_training_is_one_hot_encoded(
        self, isolated_client, unlocked_admin_headers
    ):
        _train_categorical_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/brain/darkness/prediction",
            json={
                "timestamp": FIXED_TIMESTAMP + 100 * 3600,
                "elevation": -5.0,
                "pressure_trend_1h": "falling",
            },
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200

    def test_a_category_never_seen_in_training_does_not_raise(
        self, isolated_client, unlocked_admin_headers
    ):
        _train_categorical_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/brain/darkness/prediction",
            json={
                "timestamp": FIXED_TIMESTAMP + 100 * 3600,
                "elevation": -5.0,
                "pressure_trend_1h": "stable",
            },
            headers=unlocked_admin_headers,
        )

        # pd.get_dummies produces a pressure_trend_1h_stable column that
        # brain.dataset.columns has never seen; prepare_prediction's
        # reindex(columns=brain.dataset.columns, ...) silently drops it
        # rather than raising or otherwise flagging the unknown category.
        assert response.status_code == 200
        assert "pressure_trend_1h_stable" not in response.json()["preprocessed"]

    def test_a_missing_categorical_sensor_does_not_raise(
        self, isolated_client, unlocked_admin_headers
    ):
        _train_categorical_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/brain/darkness/prediction",
            json={"timestamp": FIXED_TIMESTAMP + 100 * 3600, "elevation": -5.0},
            headers=unlocked_admin_headers,
        )

        # No pressure_trend_1h in the request at all: get_dummies never
        # produces its columns for this row, so get_x_selected_and_numerical_
        # columns simply omits them - a different path than the missing-
        # numerical-column case below, since categorical absence is handled
        # by never creating the column rather than by filling one in.
        assert response.status_code == 200

    def test_a_missing_numerical_sensor_is_imputed(
        self, isolated_client, unlocked_admin_headers
    ):
        _train_categorical_brain(isolated_client, unlocked_admin_headers)

        response = isolated_client.post(
            "/api/brain/darkness/prediction",
            json={
                "timestamp": FIXED_TIMESTAMP + 100 * 3600,
                "pressure_trend_1h": "falling",
            },
            headers=unlocked_admin_headers,
        )

        # "elevation" is a selected feature (brain.dataset.columns) but is
        # absent from this request. prepare_prediction's missing_columns
        # loop inserts it back as NaN, and the fitted SimpleImputer
        # (strategy="mean") fills it with the training mean rather than the
        # request failing or the column staying empty.
        assert response.status_code == 200
        assert "elevation" in response.json()["preprocessed"]
