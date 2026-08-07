"""Characterization tests for learninghouse.api.auth.

Every test uses `isolated_client` (see conftest.py) rather than the
session-scoped `client` fixture: these tests log in, change the admin
password and create/delete API keys, all of which mutate the shared
security database. Each test therefore gets its own brains directory, its
own fresh SecurityDatabase (admin password "learninghouse", no API keys),
and does not affect any other test in the session.
"""

from tests.conftest import DEFAULT_ADMIN_PASSWORD, admin_headers, login, unlock


class TestPostToken:
    def test_correct_password_returns_a_token_pair(self, isolated_client):
        response = isolated_client.post(
            "/api/auth/token", json={"password": DEFAULT_ADMIN_PASSWORD}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "Bearer"

    def test_wrong_password_is_rejected(self, isolated_client):
        response = isolated_client.post(
            "/api/auth/token", json={"password": "not-the-password"}
        )

        assert response.status_code == 403
        assert response.json()["error"] == "INVALID_PASSWORD"


class TestPutToken:
    def test_valid_refresh_token_returns_a_new_token_pair(self, isolated_client):
        tokens = login(isolated_client)
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}

        response = isolated_client.put("/api/auth/token", headers=headers)

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"] != tokens["refresh_token"]

    def test_missing_credentials_are_rejected(self, isolated_client):
        response = isolated_client.put("/api/auth/token")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestDeleteToken:
    def test_valid_refresh_token_is_revoked(self, isolated_client):
        tokens = login(isolated_client)
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}

        response = isolated_client.delete("/api/auth/token", headers=headers)

        assert response.status_code == 200
        assert response.json() is True

        # The revoked refresh token can no longer be redeemed for a new pair.
        response = isolated_client.put("/api/auth/token", headers=headers)
        assert response.status_code == 401

    def test_missing_credentials_still_return_true(self, isolated_client):
        # get_refresh never raises (auto_error=False) - a missing or invalid
        # refresh token is treated as "nothing to revoke", not an error.
        response = isolated_client.delete("/api/auth/token")

        assert response.status_code == 200
        assert response.json() is True


class TestDeleteTokens:
    def test_admin_token_revokes_all_refresh_tokens(
        self, isolated_client, unlocked_admin_headers
    ):
        response = isolated_client.delete(
            "/api/auth/tokens", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json() is True

    def test_missing_credentials_are_rejected(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.delete("/api/auth/tokens")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestUpdatePassword:
    def test_correct_old_password_changes_it(self, isolated_client):
        headers = admin_headers(isolated_client)

        response = isolated_client.put(
            "/api/auth/password",
            json={
                "old_password": DEFAULT_ADMIN_PASSWORD,
                "new_password": "new-password-1",
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json() is True

        # The old password no longer works, the new one does.
        assert (
            isolated_client.post(
                "/api/auth/token", json={"password": DEFAULT_ADMIN_PASSWORD}
            ).status_code
            == 403
        )
        assert (
            isolated_client.post(
                "/api/auth/token", json={"password": "new-password-1"}
            ).status_code
            == 200
        )

    def test_wrong_old_password_is_rejected(self, isolated_client):
        headers = admin_headers(isolated_client)

        response = isolated_client.put(
            "/api/auth/password",
            json={
                "old_password": "not-the-password",
                "new_password": "new-password-1",
            },
            headers=headers,
        )

        assert response.status_code == 403
        assert response.json()["error"] == "INVALID_PASSWORD"


class TestListApiKeys:
    def test_admin_token_lists_api_keys(self, isolated_client, unlocked_admin_headers):
        response = isolated_client.get(
            "/api/auth/apikeys", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_missing_credentials_are_rejected(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.get("/api/auth/apikeys")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestCreateApikey:
    def test_admin_token_creates_an_api_key(
        self, isolated_client, unlocked_admin_headers
    ):
        response = isolated_client.post(
            "/api/auth/apikey",
            json={"description": "app_as_user", "role": "user"},
            headers=unlocked_admin_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["description"] == "app_as_user"
        assert body["role"] == "user"
        assert body["key"]

    def test_duplicate_description_is_rejected(
        self, isolated_client, unlocked_admin_headers
    ):
        payload = {"description": "app_as_user", "role": "user"}
        isolated_client.post(
            "/api/auth/apikey", json=payload, headers=unlocked_admin_headers
        )

        response = isolated_client.post(
            "/api/auth/apikey", json=payload, headers=unlocked_admin_headers
        )

        assert response.status_code == 400
        assert response.json()["error"] == "APIKEY_EXISTS"


class TestDeleteApikey:
    def test_existing_key_is_deleted(self, isolated_client, unlocked_admin_headers):
        isolated_client.post(
            "/api/auth/apikey",
            json={"description": "app_as_user", "role": "user"},
            headers=unlocked_admin_headers,
        )

        response = isolated_client.delete(
            "/api/auth/apikey/app_as_user", headers=unlocked_admin_headers
        )

        assert response.status_code == 200
        assert response.json() == "app_as_user"

        listed = isolated_client.get(
            "/api/auth/apikeys", headers=unlocked_admin_headers
        )
        assert listed.json() == []

    def test_unknown_description_is_rejected(
        self, isolated_client, unlocked_admin_headers
    ):
        response = isolated_client.delete(
            "/api/auth/apikey/does_not_exist", headers=unlocked_admin_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "NO_APIKEY"


class TestRole:
    def test_admin_token_reports_admin_role(
        self, isolated_client, unlocked_admin_headers
    ):
        response = isolated_client.get("/api/auth/role", headers=unlocked_admin_headers)

        assert response.status_code == 200
        assert response.json() == "admin"

    def test_api_key_reports_its_own_role(
        self, isolated_client, unlocked_admin_headers
    ):
        created = isolated_client.post(
            "/api/auth/apikey",
            json={"description": "app_as_trainer", "role": "trainer"},
            headers=unlocked_admin_headers,
        ).json()

        response = isolated_client.get(
            "/api/auth/role", headers={"X-LEARNINGHOUSE-API-KEY": created["key"]}
        )

        assert response.status_code == 200
        assert response.json() == "trainer"

    def test_missing_credentials_are_rejected(self, isolated_client):
        unlock(isolated_client)

        response = isolated_client.get("/api/auth/role")

        assert response.status_code == 403
        assert response.json()["error"] == "SECURITY_EXCEPTION"


class TestInitialPasswordGate:
    """The EnforceInitialPasswordChange middleware, characterized through auth
    endpoints specifically: /api/auth/apikeys is not on its allow-list, so it
    stays blocked until the admin password is changed - and, since Phase 2
    fixed the routes to register unconditionally (see api/auth.py), becomes
    reachable again in the same process without a restart.
    """

    def test_apikeys_is_blocked_until_password_changed(self, isolated_client):
        headers = admin_headers(isolated_client)

        blocked = isolated_client.get("/api/auth/apikeys", headers=headers)
        assert blocked.status_code == 401
        assert blocked.json()["error"] == "UNAUTHORIZED"

        isolated_client.put(
            "/api/auth/password",
            json={
                "old_password": DEFAULT_ADMIN_PASSWORD,
                "new_password": "new-password-1",
            },
            headers=headers,
        )

        new_headers = admin_headers(isolated_client, "new-password-1")
        unblocked = isolated_client.get("/api/auth/apikeys", headers=new_headers)
        assert unblocked.status_code == 200

    def test_mode_reports_initial_before_and_normal_after(self, isolated_client):
        assert isolated_client.get("/api/mode").json() == "initial"

        headers = admin_headers(isolated_client)
        isolated_client.put(
            "/api/auth/password",
            json={
                "old_password": DEFAULT_ADMIN_PASSWORD,
                "new_password": "new-password-1",
            },
            headers=headers,
        )

        assert isolated_client.get("/api/mode").json() == "production"
