FROM python:3.11 AS buildimage

WORKDIR /learninghouse

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

COPY requirements.txt .

RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --extra-index-url https://www.piwheels.org/simple \
    -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    LHS_HOME=/learninghouse \
    LEARNINGHOUSE_HOST=0.0.0.0 \
    LEARNINGHOUSE_PORT=5000

WORKDIR /learninghouse

RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home learninghouse; \
    mkdir -p ${LHS_HOME}/brains

COPY --chown=learninghouse:learninghouse --from=buildimage /venv /venv
COPY --chown=learninghouse:learninghouse . .

EXPOSE 5000

VOLUME ["${LHS_HOME}/brains"]

USER learninghouse

CMD ["python3", "-m", "learninghouse"]
