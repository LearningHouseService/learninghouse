"""Characterization of the Phase 3b configuration.yaml / secrets.yaml
loader (docs/modernization-plan.md). Each test builds a `ServiceSettings`
directly against a fresh `tmp_path`, bypassing the process environment
entirely except where a test is specifically about the env var bootstrap.
"""

import os
import stat

import yaml

from learninghouse.core.settings.models import (
    CONFIG_DIRECTORY_ENV,
    CONFIGURATION_FILENAME,
    SECRETS_FILENAME,
    ServiceSettings,
)


def write_yaml(path, data) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle)


class TestDefaults:
    def test_defaults_apply_when_no_files_exist(self, tmp_path):
        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.host == "127.0.0.1"
        assert settings.port == 5000
        assert settings.jwt_secret

    def test_a_jwt_secret_is_generated_and_persisted(self, tmp_path):
        settings = ServiceSettings(config_directory=tmp_path)

        secrets_file = tmp_path / SECRETS_FILENAME
        assert secrets_file.exists()
        with open(secrets_file, "r", encoding="utf-8") as handle:
            persisted = yaml.safe_load(handle)
        assert persisted["jwt_secret"] == settings.jwt_secret

    def test_the_secrets_file_is_not_world_or_group_readable(self, tmp_path):
        ServiceSettings(config_directory=tmp_path)

        mode = stat.S_IMODE((tmp_path / SECRETS_FILENAME).stat().st_mode)
        assert mode == 0o600


class TestConfigurationYaml:
    def test_values_are_read_from_configuration_yaml(self, tmp_path):
        write_yaml(
            tmp_path / CONFIGURATION_FILENAME,
            {"host": "0.0.0.0", "port": 8080, "workers": 4},
        )

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.host == "0.0.0.0"
        assert settings.port == 8080
        assert settings.workers == 4

    def test_an_explicit_constructor_argument_wins_over_the_file(self, tmp_path):
        write_yaml(tmp_path / CONFIGURATION_FILENAME, {"host": "0.0.0.0"})

        settings = ServiceSettings(config_directory=tmp_path, host="192.168.1.1")

        assert settings.host == "192.168.1.1"

    def test_jwt_secret_in_configuration_yaml_is_ignored(self, tmp_path):
        write_yaml(
            tmp_path / CONFIGURATION_FILENAME, {"jwt_secret": "not-a-real-secret"}
        )

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.jwt_secret != "not-a-real-secret"

    def test_config_directory_cannot_be_set_from_inside_the_file(self, tmp_path):
        other = tmp_path / "elsewhere"
        other.mkdir()
        write_yaml(tmp_path / CONFIGURATION_FILENAME, {"config_directory": str(other)})

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.config_directory == tmp_path

    def test_an_empty_configuration_file_does_not_raise(self, tmp_path):
        (tmp_path / CONFIGURATION_FILENAME).write_text("", encoding="utf-8")

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.host == "127.0.0.1"


class TestSecretsYaml:
    def test_a_pinned_secret_is_read_and_not_overwritten(self, tmp_path):
        write_yaml(tmp_path / SECRETS_FILENAME, {"jwt_secret": "pinned-secret"})

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.jwt_secret == "pinned-secret"

    def test_the_jwt_secret_survives_across_restarts(self, tmp_path):
        first = ServiceSettings(config_directory=tmp_path)
        second = ServiceSettings(config_directory=tmp_path)

        assert first.jwt_secret == second.jwt_secret


class TestConfigDirectoryBootstrap:
    def test_the_config_directory_env_var_is_the_only_remaining_bootstrap(
        self, tmp_path
    ):
        previous = os.environ.get(CONFIG_DIRECTORY_ENV)
        os.environ[CONFIG_DIRECTORY_ENV] = str(tmp_path)
        try:
            settings = ServiceSettings()
            assert settings.config_directory == tmp_path
        finally:
            if previous is None:
                os.environ.pop(CONFIG_DIRECTORY_ENV, None)
            else:
                os.environ[CONFIG_DIRECTORY_ENV] = previous

    def test_other_learninghouse_env_vars_are_no_longer_read(self, tmp_path):
        previous = os.environ.get("LEARNINGHOUSE_HOST")
        os.environ["LEARNINGHOUSE_HOST"] = "10.0.0.1"
        try:
            settings = ServiceSettings(config_directory=tmp_path)
            assert settings.host == "127.0.0.1"
        finally:
            if previous is None:
                os.environ.pop("LEARNINGHOUSE_HOST", None)
            else:
                os.environ["LEARNINGHOUSE_HOST"] = previous


class TestDevelopmentDefaults:
    def test_development_environment_still_flips_debug_and_reload(self, tmp_path):
        write_yaml(tmp_path / CONFIGURATION_FILENAME, {"environment": "development"})

        settings = ServiceSettings(config_directory=tmp_path)

        assert settings.debug is True
        assert settings.reload is True
