# Security

The service is protected by different authentication and authorization mechanisms. For
administration you can log in via the [UI](../usage/ui.md).

## Fallback password

On the first run the service uses the fallback password `learninghouse` for the administrator
account. **Until this is changed, all other endpoints stay deactivated.**

You can change the password on the initial login screen of the UI.

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

You have to provide the API key with every request, either as a query parameter
`?api_key=YOURSECRETKEY` or as a header field `X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY`. Prefer the
header - query strings end up in access logs, proxy logs and browser history.

You can also test the API key by logging in to the UI.

## The JWT secret

After an administration login the service issues a JWT, signed with `jwt_secret` from
`secrets.yaml`. That file is generated on first start and written with mode `0600`, so sessions
survive a service restart. See the [configuration reference](index.md#secretsyaml).

`jwt_expire_minutes` (default: 10) controls how long a refresh token stays valid.
