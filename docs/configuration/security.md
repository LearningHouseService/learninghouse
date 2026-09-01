# Security

The service is protected by different authentication and authorization mechanisms. For
administration you can log in via the [UI](../usage/ui.md).

## Fallback password

On the first run the service uses the fallback password `learninghouse` for the administrator
account. **Until this is changed, all other endpoints stay deactivated.**

You can change the password on the initial login screen of the UI.

The password is stored as an [argon2id](https://en.wikipedia.org/wiki/Argon2) hash, never in clear
text.

!!! danger "Credentials from an earlier release are not carried over"
    The old hashes (`sha512_crypt`) are not read any more, and nothing migrates them. After the
    upgrade the administration account is back on the fallback password `learninghouse` and there
    are **no API keys**. Log in, set a new password, create the API keys again and update your
    clients. Every endpoint outside login stays deactivated until the password is changed. See
    [decision 0006](../decisions/0006-argon2id-passwords-and-hashed-api-keys.md).

!!! warning "Use a separate password"
    Unless you use a proxy setup for SSL security of your connection, only use a separate password
    for your learningHouse.

## API keys

You can use your administration access for training and prediction endpoints, but we also
recommend using an API key for application access. There are two roles for API key authorization:

| Role | Allowed endpoints |
|---|---|
| `user` | prediction |
| `trainer` | training and prediction |

You can add more API keys via the UI.

!!! danger "The key is shown once"
    Your API key is only displayed once and cannot be requested again, so save it. If you forget
    it you have to delete that API key and create a new one.

You have to provide the API key with every request, as the header field
`X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY`.

You can also test the API key by logging in to the UI.

!!! danger "`?api_key=` is deprecated and rejected"
    Query strings end up in access logs, proxy logs and browser history, so a key sent that way
    has to be considered leaked. A request carrying only `?api_key=` is answered with `403` and
    the error `APIKEY_IN_QUERY`.

    If a client of yours still needs it, set `allow_api_key_query: true` in `configuration.yaml`
    for as long as it takes to move that client to the header. Every request accepted this way
    logs a warning naming the key as compromised. The header always wins when both are present.

Keys are stored as a salted SHA-256 hash, so the stored form cannot be read back into working keys
- and neither can you: keys created by a release before argon2id are not carried over and have to
be created again.

A rejected key is logged as a warning, without the key itself, so repeated attempts against your
instance are visible.

## CORS

Browsers only let a page on one origin call a service on another when the service says it may.
The service answers those requests with credentials, so the list of origins it accepts is
explicit:

```yaml
cors_allowed_origins:
  - https://home.example
  - http://homeassistant.local:8123
```

Leaving it out is the normal case. The service's own origin - `base_url` if you set one,
otherwise `host` and `port` - is always allowed, and that is where the bundled
[UI](../usage/ui.md) is served from. The UI works without configuring anything, and a page on any
other origin does not. In the development environment `http://localhost:4200` is allowed too, for
Angular's `ng serve`.

!!! danger "`*` is refused"
    A wildcard next to credentials means every web page your browser visits can call your
    learningHouse with your session. The service refuses to start with `*` in the list. Name the
    origins that actually need access instead.

## The JWT secret

After an administration login the service issues a JWT, signed with `jwt_secret` from
`secrets.yaml`. That file is generated on first start and written with mode `0600`, so sessions
survive a service restart. See the [configuration reference](index.md#secretsyaml).

`jwt_expire_minutes` (default: 10) controls how long a refresh token stays valid.

The first start writes a freshly generated secret and logs a warning saying so. Keep `secrets.yaml`
with your backups: losing it logs everyone out, and it is the one value that has to survive a
restart for sessions to.
