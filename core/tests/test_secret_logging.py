"""No secret, token or API key may appear in log output, at any level.

Every test attaches a loguru sink at DEBUG - the most verbose level the
service can be run at - collects everything the service writes while a full
administration flow runs, and then looks for the values that must never be
there.
"""

from contextlib import contextmanager

from loguru import logger

from tests.conftest import DEFAULT_ADMIN_PASSWORD, admin_headers, unlock

ADMIN_PASSWORD = "a-password-that-appears-nowhere-else"


@contextmanager
def capture_logs():
    """Collect everything written through loguru while the block runs.

    Has to be entered *after* the application is built: `get_application`
    calls `initialize_logging`, which reconfigures loguru and drops every
    handler attached before it - including this sink.
    """
    records = []
    sink_id = logger.add(records.append, level="DEBUG")

    try:
        yield records
    finally:
        logger.remove(sink_id)


def captured(records) -> str:
    return "".join(records)


class TestJwtSecretGeneration:
    def test_the_generated_secret_is_not_logged_only_its_file(self, tmp_path):
        from learninghouse.core.settings.models import ServiceSettings

        with capture_logs() as records:
            settings = ServiceSettings(config_directory=tmp_path)

        output = captured(records)
        assert "secrets.yaml" in output
        assert settings.jwt_secret not in output


class TestAdministrationFlow:
    def test_no_password_token_or_api_key_reaches_the_log(self, configured_client):
        client = configured_client(logging_level="DEBUG")

        from learninghouse.core.settings import service_settings

        jwt_secret = service_settings().jwt_secret

        with capture_logs() as records:
            headers = admin_headers(client)
            assert (
                client.put(
                    "/api/auth/password",
                    json={
                        "old_password": DEFAULT_ADMIN_PASSWORD,
                        "new_password": ADMIN_PASSWORD,
                    },
                    headers=headers,
                ).status_code
                == 200
            )

            headers = admin_headers(client, ADMIN_PASSWORD)
            tokens = client.post(
                "/api/auth/token", json={"password": ADMIN_PASSWORD}
            ).json()
            api_key = client.post(
                "/api/auth/apikey",
                json={"description": "app_as_user", "role": "user"},
                headers=headers,
            ).json()["key"]

            assert (
                client.get(
                    "/api/auth/role", headers={"X-LEARNINGHOUSE-API-KEY": api_key}
                ).status_code
                == 200
            )
            client.get("/api/auth/apikeys", headers=headers)
            client.delete(
                "/api/auth/apikey/app_as_user",
                headers=admin_headers(client, ADMIN_PASSWORD),
            )

        output = captured(records)

        # The flow really did run through this sink.
        assert "Admin user logged in sucessfully" in output

        for secret in (
            ADMIN_PASSWORD,
            api_key,
            jwt_secret,
            tokens["access_token"],
            tokens["refresh_token"],
        ):
            assert secret not in output

    def test_a_rejected_api_key_is_logged_but_never_echoed(self, configured_client):
        """A rejected credential has to leave a trace - guessing is bounded by
        the request rate, not by the hash, so somebody trying keys should be
        visible in the log. The trace must not contain the key itself.
        """
        client = configured_client(logging_level="DEBUG")
        # EnforceInitialPasswordChange would answer before authentication
        # runs at all while the admin password is still the fallback one.
        unlock(client)

        with capture_logs() as records:
            client.get(
                "/api/auth/role", headers={"X-LEARNINGHOUSE-API-KEY": "wrong-key"}
            )

        output = captured(records)
        assert "Rejected an unknown API key" in output
        assert "header" in output
        assert "wrong-key" not in output

    def test_a_rejected_password_is_logged_but_never_echoed(self, configured_client):
        client = configured_client(logging_level="DEBUG")

        with capture_logs() as records:
            client.post("/api/auth/token", json={"password": "wrong-password"})

        output = captured(records)
        assert "Rejected an administration login" in output
        assert "wrong-password" not in output
