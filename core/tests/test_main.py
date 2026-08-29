"""The startup path in `learninghouse.__main__`.

`workers` above 1 has to be rejected at startup *with an explanation*, so the
explanation itself is what these tests pin, not just the fact that the
settings refuse the value.
"""

import os
import subprocess
import sys

import pytest
import yaml
from pydantic import ValidationError

from learninghouse.__main__ import report_invalid_configuration
from learninghouse.core.settings.models import CONFIGURATION_FILENAME, ServiceSettings


def write_configuration(directory, data) -> None:
    with open(directory / CONFIGURATION_FILENAME, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle)


class TestReportInvalidConfiguration:
    def test_it_names_the_setting_and_the_reason(self, tmp_path, capsys):
        write_configuration(tmp_path, {"workers": 4})

        with pytest.raises(ValidationError) as excinfo:
            ServiceSettings(config_directory=tmp_path)

        assert report_invalid_configuration(excinfo.value) == 1

        error_output = capsys.readouterr().err
        assert "workers: workers must be 1 for now" in error_output
        assert "held per process" in error_output
        # No pydantic frames, no "Value error," prefix, and a place to read on.
        assert "Value error," not in error_output
        assert "learninghouse/configuration/" in error_output

    def test_a_wildcard_origin_is_reported_the_same_way(self, tmp_path, capsys):
        write_configuration(tmp_path, {"cors_allowed_origins": ["*"]})

        with pytest.raises(ValidationError) as excinfo:
            ServiceSettings(config_directory=tmp_path)

        report_invalid_configuration(excinfo.value)

        error_output = capsys.readouterr().err
        assert "cors_allowed_origins" in error_output
        assert "credentials" in error_output


class TestStartup:
    """The one place the whole path is exercised: a real process, started the
    way the Docker image starts it, against a configuration it must refuse.
    """

    def test_workers_above_one_exits_with_the_explanation(self, tmp_path):
        write_configuration(tmp_path, {"workers": 4})

        result = subprocess.run(
            [sys.executable, "-m", "learninghouse"],
            env={**os.environ, "LEARNINGHOUSE_CONFIG_DIRECTORY": str(tmp_path)},
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        assert result.returncode == 1
        assert "learningHouse cannot start" in result.stderr
        assert "held per process" in result.stderr
        # The refusal has to read as temporary - see decision 0007.
        assert "comes back" in result.stderr
        assert "Traceback" not in result.stderr
