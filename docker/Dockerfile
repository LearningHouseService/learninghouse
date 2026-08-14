# syntax=docker/dockerfile:1
FROM python:3.13-slim AS buildimage

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    UV_PROJECT_ENVIRONMENT=/venv \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY --from=ghcr.io/astral-sh/uv:0.12.4 /uv /usr/local/bin/uv

# Dependencies come straight from the lockfile, cached by BuildKit across
# builds and independent of the wheel below — only pyproject.toml or uv.lock
# changing invalidates this layer, not every release.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-install-project

# The wheel carries the actual package — UI and the version determined by
# setuptools-scm already baked in — and installs on top of the dependencies
# synced above with --no-deps, so the image needs neither a source tree nor
# git history, and this layer alone changes on every release.
COPY dist/*.whl /build/
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --no-deps /build/*.whl

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    LHS_HOME=/learninghouse \
    LEARNINGHOUSE_HOST=0.0.0.0 \
    LEARNINGHOUSE_PORT=5000

WORKDIR /learninghouse

RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home learninghouse; \
    mkdir -p ${LHS_HOME}/brains; \
    chown -R learninghouse:learninghouse ${LHS_HOME}

COPY --chown=learninghouse:learninghouse --from=buildimage /venv /venv

EXPOSE 5000

VOLUME ["${LHS_HOME}/brains"]

USER learninghouse

CMD ["python3", "-m", "learninghouse"]
