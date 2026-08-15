"""One-shot migration from LEARNINGHOUSE_* environment variables to
configuration.yaml / secrets.yaml (docs/modernization-plan.md, Phase 3b).

Run once, by hand, on upgrade - not on every start. Only migrates settings;
it does not touch brain data, sensors or the security database.
"""

import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from learninghouse.core.settings.models import (
    CONFIGURATION_FILENAME,
    SECRET_FIELDS,
    SECRETS_FILENAME,
)

ENV_PREFIX = "learninghouse_"


def _strip_prefix(key: str) -> str:
    return key.lower().strip()[len(ENV_PREFIX) :]


def read_dotenv(dotenv_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}

    if not dotenv_path.exists():
        return values

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key.lower().startswith(ENV_PREFIX):
            values[_strip_prefix(key)] = value.strip()

    return values


def read_environment(environ: Dict[str, str]) -> Dict[str, str]:
    return {
        _strip_prefix(key): value.strip()
        for key, value in environ.items()
        if key.lower().startswith(ENV_PREFIX)
    }


def collect_settings(dotenv_path: Path, environ: Dict[str, str]) -> Dict[str, str]:
    # dotenv first, environment overrides - matches the precedence the
    # settings loader this replaces used to have (environment read before
    # dotenv, first-write-wins).
    values = read_dotenv(dotenv_path)
    values.update(read_environment(environ))

    # The bootstrap value, not migrated content: it says where this very
    # pair of files goes, it cannot also be a key inside them.
    values.pop("config_directory", None)

    return values


def split_secrets(values: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    configuration: Dict[str, Any] = {}
    secrets: Dict[str, Any] = {}

    for key, value in values.items():
        if key in SECRET_FIELDS:
            secrets[key] = value
        else:
            configuration[key] = value

    return configuration, secrets


def _write_yaml(file_path: Path, data: Dict[str, Any], force: bool) -> None:
    if file_path.exists() and not force:
        raise FileExistsError(
            f"{file_path} already exists, pass --force to overwrite it"
        )

    with open(file_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def migrate(
    config_directory: Path, dotenv_path: Path, environ: Dict[str, str], force: bool
) -> Tuple[Path, Optional[Path]]:
    values = collect_settings(dotenv_path, environ)
    configuration, secrets = split_secrets(values)

    config_directory.mkdir(parents=True, exist_ok=True)

    configuration_path = config_directory / CONFIGURATION_FILENAME
    _write_yaml(configuration_path, configuration, force)

    secrets_path = None
    if secrets:
        secrets_path = config_directory / SECRETS_FILENAME
        _write_yaml(secrets_path, secrets, force)
        secrets_path.chmod(0o600)

    return configuration_path, secrets_path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="learninghouse-migrate-config",
        description=(
            "Migrate LEARNINGHOUSE_* environment variables (and a .env file, "
            "if present) into a configuration.yaml / secrets.yaml pair. "
            "Does not touch brain data, sensors or the security database."
        ),
    )
    parser.add_argument(
        "--config-directory",
        type=Path,
        default=Path("./brains"),
        help="Target directory for configuration.yaml / secrets.yaml (default: brains)",
    )
    parser.add_argument(
        "--dotenv",
        type=Path,
        default=Path(".env"),
        help="Path to a .env file to read alongside the process environment",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing configuration.yaml / secrets.yaml",
    )
    args = parser.parse_args()

    try:
        configuration_path, secrets_path = migrate(
            args.config_directory, args.dotenv, dict(os.environ), args.force
        )
    except FileExistsError as error:
        raise SystemExit(str(error)) from error

    print(f"Wrote {configuration_path}")
    if secrets_path is not None:
        print(f"Wrote {secrets_path}")


if __name__ == "__main__":
    main()
