# 1. uv for the Python build and the Docker image

- **Status:** accepted
- **Date:** 2026-08-14

## Context

The Python side installed with `pip install -e ".[dev]"` and built with `pip install build &&
python -m build`. CI cached `~/.cache/pip` through a hand-written `actions/cache` block keyed on
`pyproject.toml`'s hash. Dependencies were declared in `pyproject.toml` and nowhere else, so
"reproducible" meant whatever pip resolved on the day - a transitive dependency could change
between two runs of the same commit without a single tracked file changing.

The Docker image installed with `pip` into a virtualenv, in one layer, from an index list that
included [piwheels](https://www.piwheels.org/) - present only to serve prebuilt `armv6l`/`armv7l`
wheels for `numpy`, `scipy` and `scikit-learn`.

The next phase of work was going to re-pin every shared dependency against
[pvlearn](https://github.com/LearningHouseService/pvlearn) (see
[0003](0003-exact-pins-shared-with-pvlearn.md)). Pinning with pip first and moving the result to a
lockfile afterwards would have meant doing that work twice.

## Decision

`pyproject.toml` stays the single source of truth for dependencies, and a committed `core/uv.lock`
records what they actually resolve to.

- **CI** uses `astral-sh/setup-uv` with `enable-cache: true` and
  `cache-dependency-glob: "core/uv.lock"`, then `uv sync --locked` and `uv run`. `--locked` fails
  the build when the lockfile and `pyproject.toml` disagree, so a pin cannot be edited without
  updating the lockfile in the same commit. `save-cache` is `${{ github.event_name !=
  'pull_request' }}`: a cache written by a pull request run is only ever read back by a re-run of
  that same pull request, so writing one on every push is cache-quota spend for no reuse.
- **The Docker image** builds in two layers instead of one. `uv sync --frozen
  --no-install-project` installs everything the lockfile pins, under a BuildKit
  `--mount=type=cache` so the download cache survives across builds; the wheel is then installed on
  top with `uv pip install --no-deps`. A dependency change and a version-only rebuild invalidate
  different layers. `--no-deps` is what keeps the second layer from re-resolving the wheel's
  metadata and drifting off the lockfile's pins.
- **`piwheels` is dropped entirely.** `uv`'s resolver made the reason explicit: the index lists
  `numpy` for `linux_armv6l`/`linux_armv7l` only, not for the platform actually being built.
  `armv7` is excluded as a target, so keeping the index would have meant carrying a `uv`-specific
  `--index-strategy unsafe-best-match` workaround for wheels the image never asks for.
- **The image installs a wheel, not a source tree.** The wheel already contains the built Angular
  UI and the version `setuptools-scm` derived from git, so the image needs neither a source tree
  nor git history.

## Consequence

Dropping `armv7` removed the last reason to wait on multi-architecture builds: `numpy`, `pandas`,
`scikit-learn` and `scipy` all publish `manylinux_aarch64` wheels for `cp313` at the pinned
versions, so an `arm64` build compiles nothing. `build-docker` became a `linux/amd64` /
`linux/arm64` matrix on native runners (`ubuntu-latest` / `ubuntu-24.04-arm`, both free for a
public repository), each leg exporting its image digest, with a `merge-manifest` job combining
them. QEMU emulation was dropped rather than kept as a fallback.

The manifest is assembled **by digest**, not by the mutable per-arch tags. Two overlapping
workflow runs - the slower `arm64` leg of an older commit finishing after a newer commit's push -
would otherwise let the older image win the final multi-arch tag silently.

Anyone bumping a Python dependency now edits two files, `pyproject.toml` and `uv.lock`, and CI
rejects the pull request if they edit only one. This is also what made the `pip` Dependabot
ecosystem unusable for this repository; see
[0004](0004-dependabot-groups-for-framework-majors.md).
