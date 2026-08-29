# The web UI

For configuration purposes there is a small user interface. With the service running, it is at
<http://localhost:5000/ui>.

Use it to:

- Log in with the administration account and change its password. Until the
  [fallback password](../configuration/security.md#fallback-password) is changed, every other
  endpoint stays disabled.
- Declare your [sensors](../configuration/sensors.md) and their data types.
- Create and configure [brains](../configuration/brains.md).
- Create [API keys](../configuration/security.md#api-keys) with the `user` or `trainer` role, and
  test them.

The UI is shipped inside the Python package and the Docker image; there is nothing separate to
install or serve.
