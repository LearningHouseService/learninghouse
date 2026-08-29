# 5. The documentation site is built from `core/`, and published on release only

- **Status:** accepted
- **Date:** 2026-08-29

## Context

Everything a user needed - configuration keys, the migration script from
[0002](0002-yaml-configuration-with-a-one-shot-migration.md), sensor and brain configuration,
training and prediction examples, Docker instructions - lived in one 310-line `README.md`, read on
a repository page. No navigation, no search, no dead-link checking, and a change to any of it was
invisible in review beyond the diff.

Three planned phases each add pages to that file: CORS and session settings, a change to where
data lives, and a Home Assistant add-on with its own installation path. Splitting the README after
them means writing the same pages twice.

The repository has an awkward shape for a documentation site. The Python lives in `core/`, with
its own `pyproject.toml` and `uv.lock`; `docs/` sits at the repository root, next to the plan that
is not user documentation.

## Decision

The site is MkDocs Material, built from `docs/`, with `mkdocs.yml` at the repository root.

- **The documentation dependencies are a `docs` extra of `core/pyproject.toml`**, pinned exactly
  like `dev` and resolved through `core/uv.lock`. The build therefore runs from `core/`:
  `uv run mkdocs build --strict --config-file ../mkdocs.yml`. A second `pyproject.toml` and
  lockfile at the root, holding two packages, was rejected - it would be the only Python project
  outside `core/` and would need its own dependency updates, its own Dependabot ecosystem and its
  own cache key, all for `mkdocs` and `mkdocs-material`. The versions match what
  `solaredge2mqtt` pins, so the two sibling sites render with the same theme release.
- **`validation` treats a dead link as an error, anchors included.** `unrecognized_links: warn`
  plus `anchors: warn` under `--strict` means a link to a heading somebody renamed fails the build
  instead of quietly landing at the top of the page. The same setting makes a `nav` entry pointing
  at a missing file, and a page in `docs/` that no `nav` entry points at, both build failures.
- **Working documents are excluded via `not_in_nav`.** Planning notes are written for the people
  doing the work and read as unfinished promises to anybody else. Naming such a file there rather
  than leaving it unmentioned is what the previous point requires: `--strict` fails on an
  unreferenced page, so the exclusion has to be explicit. What survives such a document is a
  decision record in this series, not a link to it.
- **The API is not restated.** The service serves its own OpenAPI document at `/docs`, generated
  from the code that handles the requests. A second, hand-written endpoint list on the site would
  be stale the first time a route changes, and nothing would fail when it did.
- **CI builds the site on every push and pull request** and uploads the rendered `site/` as an
  artifact, so a documentation change can be reviewed as a browsable site rather than as Markdown.
  The job mirrors `check-core`'s uv setup exactly - same action version, `core/uv.lock` as the
  cache key, and the `save-cache` rule from [0001](0001-uv-for-the-python-build.md). It checks out
  with full history because `uv sync` installs the project itself, and `setuptools-scm` derives
  the version from the repository's tags.
- **Pages deployment happens on `release` only**, after the jobs that publish what the site
  describes: the package to PyPI and the release assets, and the multi-arch image manifest.

## Consequence

Publishing on release rather than on every push to `main` means the site can lag `main` by up to
one release. That is the point: `main` carries documentation for code that is not installable yet,
and a page describing a version nobody can install is worse than a page describing the previous
one. The reviewable artifact from every run covers the gap for the people who need it.

The deployment job queues rather than cancels - `concurrency: group: pages` with
`cancel-in-progress: false`. GitHub Pages allows one deployment at a time, and a cancelled one
leaves the site on the previous version, so two releases in quick succession must not race.

`actions/configure-pages` runs with `enablement: true`, so the first release switches Pages on for
the repository instead of failing on a setting nobody remembered to click.

The README keeps only what a repository page is for: badges, what the service does, the feature
list, a quick start, and a link to the site. Anything else added to it in future belongs on a
page, and the split only holds if that rule is applied to the next change as well as this one.
