"""Characterization of `learninghouse-migrate-config`
(docs/modernization-plan.md, Phase 3b): converts LEARNINGHOUSE_* environment
variables (plus an optional .env file) into a configuration.yaml /
secrets.yaml pair, without touching anything else.
"""

import pytest
import yaml

from learninghouse.scripts.migrate_config import (
    collect_settings,
    migrate,
    read_dotenv,
    split_secrets,
)


class TestReadDotenv:
    def test_reads_prefixed_keys_and_ignores_the_rest(self, tmp_path):
        dotenv = tmp_path / ".env"
        dotenv.write_text(
            "\n".join(
                [
                    "# a comment",
                    "LEARNINGHOUSE_HOST=0.0.0.0",
                    "LEARNINGHOUSE_PORT=8080",
                    "SOME_OTHER_VAR=ignored",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        values = read_dotenv(dotenv)

        assert values == {"host": "0.0.0.0", "port": "8080"}

    def test_a_missing_file_yields_no_values(self, tmp_path):
        assert read_dotenv(tmp_path / "does-not-exist.env") == {}


class TestCollectSettings:
    def test_environment_overrides_dotenv(self, tmp_path):
        dotenv = tmp_path / ".env"
        dotenv.write_text("LEARNINGHOUSE_HOST=0.0.0.0\n", encoding="utf-8")

        values = collect_settings(dotenv, {"LEARNINGHOUSE_HOST": "10.0.0.1"})

        assert values["host"] == "10.0.0.1"

    def test_config_directory_is_never_migrated_as_a_setting(self, tmp_path):
        values = collect_settings(
            tmp_path / ".env", {"LEARNINGHOUSE_CONFIG_DIRECTORY": "/somewhere"}
        )

        assert "config_directory" not in values


class TestSplitSecrets:
    def test_jwt_secret_goes_to_secrets_the_rest_to_configuration(self):
        configuration, secrets = split_secrets(
            {"host": "0.0.0.0", "jwt_secret": "s3cr3t"}
        )

        assert configuration == {"host": "0.0.0.0"}
        assert secrets == {"jwt_secret": "s3cr3t"}


class TestMigrate:
    def test_writes_a_correct_configuration_and_secrets_pair(self, tmp_path):
        target = tmp_path / "brains"
        environ = {
            "LEARNINGHOUSE_HOST": "0.0.0.0",
            "LEARNINGHOUSE_PORT": "8080",
            "LEARNINGHOUSE_JWT_SECRET": "s3cr3t",
            "LEARNINGHOUSE_CONFIG_DIRECTORY": "/should-not-appear",
        }

        configuration_path, secrets_path = migrate(
            target, tmp_path / ".env", environ, force=False
        )

        assert secrets_path is not None

        with open(configuration_path, "r", encoding="utf-8") as handle:
            configuration = yaml.safe_load(handle)
        with open(secrets_path, "r", encoding="utf-8") as handle:
            secrets = yaml.safe_load(handle)

        assert configuration == {"host": "0.0.0.0", "port": "8080"}
        assert secrets == {"jwt_secret": "s3cr3t"}

    def test_no_secrets_file_is_written_when_there_is_nothing_sensitive(self, tmp_path):
        target = tmp_path / "brains"

        _, secrets_path = migrate(
            target, tmp_path / ".env", {"LEARNINGHOUSE_HOST": "0.0.0.0"}, force=False
        )

        assert secrets_path is None
        assert not (target / "secrets.yaml").exists()

    def test_refuses_to_overwrite_without_force(self, tmp_path):
        target = tmp_path / "brains"
        migrate(
            target, tmp_path / ".env", {"LEARNINGHOUSE_HOST": "0.0.0.0"}, force=False
        )

        with pytest.raises(FileExistsError):
            migrate(
                target,
                tmp_path / ".env",
                {"LEARNINGHOUSE_HOST": "10.0.0.1"},
                force=False,
            )

        with open(target / "configuration.yaml", "r", encoding="utf-8") as handle:
            configuration = yaml.safe_load(handle)
        assert configuration == {"host": "0.0.0.0"}

    def test_force_overwrites_an_existing_pair(self, tmp_path):
        target = tmp_path / "brains"
        migrate(
            target, tmp_path / ".env", {"LEARNINGHOUSE_HOST": "0.0.0.0"}, force=False
        )

        migrate(
            target, tmp_path / ".env", {"LEARNINGHOUSE_HOST": "10.0.0.1"}, force=True
        )

        with open(target / "configuration.yaml", "r", encoding="utf-8") as handle:
            configuration = yaml.safe_load(handle)
        assert configuration == {"host": "10.0.0.1"}
