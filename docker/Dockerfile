FROM python:3.13 AS buildimage

COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /usr/local/bin/uv

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# The wheel carries the pinned dependencies, the UI and the version determined
# by setuptools-scm, so the image needs neither a source tree nor git history.
COPY dist/*.whl /build/

# --index-strategy unsafe-best-match: piwheels only carries wheels for arm
# platforms, not this amd64 build stage. uv's default index strategy stops at
# the first index that lists a package name at all, regardless of whether it
# has a matching wheel, and piwheels does list numpy here — just not for this
# platform. pip's own extra-index-url behaviour falls through to PyPI in that
# case; this flag restores it. Safe here because every dependency is an exact
# pin from the wheel's own metadata, not a loose range.
RUN uv venv /venv && \
    uv pip install \
    --python /venv/bin/python \
    --no-cache \
    --extra-index-url https://www.piwheels.org/simple \
    --index-strategy unsafe-best-match \
    /build/*.whl

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
