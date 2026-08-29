"""Password and API key hashing in `learninghouse.models.auth`, see
docs/decisions/0006-argon2id-passwords-and-hashed-api-keys.md.

Passwords are argon2id, API keys a salted SHA-256. Neither format written by
an earlier release (sha512_crypt, `$6$...`) can be read any more: a database
carrying them has its administration password reset to the fallback and its
API keys removed, once, on load.

`_security_filename` is patched per test: `SecurityDatabase.write()` resolves
it through the process-wide settings otherwise, and these tests deliberately
write the database to disk to show the reset is persisted.
"""

import json

import pytest

from learninghouse.models.auth import (
    API_KEY_BYTES,
    API_KEY_HASH_PREFIX,
    INITIAL_ADMIN_PASSWORD,
    APIKey,
    APIKeyRequest,
    APIKeyRole,
    SecurityDatabase,
)

SALT = "0123456789abcdef"

# A hash in passlib's sha512_crypt format. Its content is irrelevant - the
# code only detects the format and refuses to read it, which is the whole
# point of dropping the dependency that could.
LEGACY_PASSWORD_HASH = "$6$rounds=535000$0123456789abcdef$Nx4ck.LegacyHashValue"
LEGACY_API_KEY_HASH = "$6$rounds=535000$0123456789abcdef$Zz9pQ.LegacyKeyValue"


@pytest.fixture()
def security_file(tmp_path, monkeypatch):
    filename = tmp_path / "security.json"
    monkeypatch.setattr(
        "learninghouse.models.auth._security_filename", lambda: filename
    )
    return filename


def write_legacy_database(filename, with_api_key: bool = True) -> None:
    """Write a security.json in the format an earlier release produced."""
    content = {
        "admin_password": LEGACY_PASSWORD_HASH,
        "api_keys": {},
        "salt": SALT,
        "rounds": 535000,
        "initial_password": False,
    }

    if with_api_key:
        content["api_keys"][LEGACY_API_KEY_HASH] = {
            "description": "app_as_user",
            "role": "user",
            "key": LEGACY_API_KEY_HASH,
        }

    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(content, handle)


class TestPasswordHashing:
    def test_a_new_database_hashes_the_fallback_password_with_argon2(
        self, security_file
    ):
        database = SecurityDatabase.load_or_write_default()

        assert database.admin_password.startswith("$argon2")
        assert database.authenticate_password("learninghouse") is True

    def test_a_wrong_password_is_rejected(self, security_file):
        database = SecurityDatabase.load_or_write_default()

        assert database.authenticate_password("not-the-password") is False

    def test_an_updated_password_is_stored_as_argon2(self, security_file):
        database = SecurityDatabase.load_or_write_default()

        database.update_password("a-new-password")

        assert database.admin_password.startswith("$argon2")
        assert database.initial_password is False
        assert database.authenticate_password("a-new-password") is True


class TestLegacyDatabaseIsReset:
    """A database in the old format is not migrated, it is emptied of
    credentials - see the module docstring. This is the breaking half of the
    hashing change, and the reason `passlib` is gone rather than kept for
    verification.
    """

    def test_the_admin_password_falls_back_to_the_initial_one(self, security_file):
        write_legacy_database(security_file)

        database = SecurityDatabase.load_or_write_default()

        assert database.admin_password.startswith("$argon2")
        assert database.authenticate_password(INITIAL_ADMIN_PASSWORD) is True

    def test_the_initial_password_gate_is_armed_again(self, security_file):
        # Every endpoint outside the login/password allow-list stays blocked
        # until an administrator sets a new password.
        write_legacy_database(security_file)

        database = SecurityDatabase.load_or_write_default()

        assert database.initial_password is True

    def test_legacy_api_keys_are_removed(self, security_file):
        write_legacy_database(security_file)

        database = SecurityDatabase.load_or_write_default()

        assert database.api_keys == {}
        assert database.list_api_keys() == []

    def test_the_reset_is_written_back_once(self, security_file):
        write_legacy_database(security_file)

        SecurityDatabase.load_or_write_default()
        reloaded = SecurityDatabase.load_or_write_default()

        # The second load finds nothing left to reset, so a password set in
        # between would survive - the reset does not repeat on every start.
        assert reloaded.reset_legacy_credentials() is False
        assert "$6$" not in security_file.read_text(encoding="utf-8")

    def test_a_current_database_is_left_alone(self, security_file):
        database = SecurityDatabase.load_or_write_default()
        database.update_password("a-new-password")
        created = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )
        database.write()

        reloaded = SecurityDatabase.load_or_write_default()

        assert reloaded.reset_legacy_credentials() is False
        assert reloaded.initial_password is False
        assert reloaded.authenticate_password("a-new-password") is True
        assert reloaded.find_apikey_by_key(created.key) is not None


class TestApiKeyHashing:
    def test_a_created_key_is_stored_as_a_salted_sha256(self, security_file):
        database = SecurityDatabase.load_or_write_default()

        created = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )

        stored = list(database.api_keys)
        assert len(stored) == 1
        assert stored[0].startswith(API_KEY_HASH_PREFIX)
        # The raw key is returned once and never stored.
        assert created.key not in stored

    def test_a_created_key_is_found_again(self, security_file):
        database = SecurityDatabase.load_or_write_default()
        created = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )

        found = database.find_apikey_by_key(created.key)

        assert found is not None
        assert found.description == "app_as_user"

    def test_an_unknown_key_is_not_found(self, security_file):
        database = SecurityDatabase.load_or_write_default()
        database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )

        assert database.find_apikey_by_key("00000000000000000000000000000000") is None


class TestLegacyApiKeyIsNotAccepted:
    def test_a_key_hashed_by_an_earlier_release_no_longer_authenticates(
        self, security_file
    ):
        write_legacy_database(security_file)
        database = SecurityDatabase.load_or_write_default()

        # Even the raw key that produced the stored hash is worthless now:
        # the entry is gone, and its owner has to create a new key.
        assert database.find_apikey_by_key("the-old-key") is None

    def test_a_stray_legacy_entry_is_dropped_without_touching_current_ones(
        self, security_file
    ):
        database = SecurityDatabase.load_or_write_default()
        created = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )
        database.api_keys[LEGACY_API_KEY_HASH] = APIKey(
            description="app_as_trainer",
            role=APIKeyRole.TRAINER,
            key=LEGACY_API_KEY_HASH,
        )

        assert database.reset_legacy_credentials() is True
        assert list(database.api_keys) == [database.hash_api_key(created.key)]


class TestApiKeyEntropy:
    """The condition the API key hashing rests on.

    A salted SHA-256 is the right construction for a key of 128 random bits
    generated by the service, and the wrong one for a secret a person may
    choose. Neither half of that is enforced by the hashing code itself, so
    it is enforced here: if a future change lets a client bring its own key,
    or shortens the generated one, these tests fail and the hash choice has
    to be revisited (docs/decisions/0006-argon2id-passwords-and-hashed-api-
    keys.md).
    """

    def test_a_generated_key_carries_at_least_128_bits(self, security_file):
        database = SecurityDatabase.load_or_write_default()

        created = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )

        assert API_KEY_BYTES >= 16
        assert len(bytes.fromhex(created.key)) == API_KEY_BYTES

    def test_two_keys_are_not_the_same(self, security_file):
        database = SecurityDatabase.load_or_write_default()

        first = database.create_apikey(
            APIKeyRequest(description="app_as_user", role=APIKeyRole.USER)
        )
        second = database.create_apikey(
            APIKeyRequest(description="app_as_trainer", role=APIKeyRole.TRAINER)
        )

        assert first.key != second.key

    def test_a_client_cannot_choose_its_own_key(self):
        # The request model carries no key field, so there is no route by
        # which a caller-supplied secret reaches hash_api_key.
        assert "key" not in APIKeyRequest.model_fields
