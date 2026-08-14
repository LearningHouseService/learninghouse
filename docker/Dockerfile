FROM python:3.13 AS buildimage

COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /usr/local/bin/uv

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# The wheel carries the pinned dependencies, the UI and the version determined
# by setuptools-scm, so the image needs neither a source tree nor git history.
COPY dist/*.whl /build/

RUN uv venv /venv && \
    uv pip install \
    --python /venv/bin/python \
    --no-cache \
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
