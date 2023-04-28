FROM python:3.10-slim AS buildimage

COPY container/requirements.txt requirements.txt

RUN set -eux; \
    pip3 wheel \
    --wheel-dir=/root/wheels \
    --extra-index-url https://www.piwheels.org/simple \
    -r requirements.txt

FROM python:3.10-slim

ENV LHS_HOME=/learninghouse \
    USER_ID=9002 \
    GROUP_ID=9002 \
    LEARNINGHOUSE_HOST=0.0.0.0 \
    LEARNINGHOUSE_PORT=5000

COPY --from=buildimage /root/wheels /root/wheels
COPY container/*.whl /root/wheels
COPY entrypoint.sh /

RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    gosu \
    tini; \
    ln -s -f $(which gosu) /usr/local/bin/gosu; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    mkdir -p ${LHS_HOME}/brains; \
    cd ${LHS_HOME}; \
    pip3 install \
    --no-index \
    --find-links=/root/wheels \
    learninghouse; \
    chmod +x /entrypoint.sh; \
    rm -rf /root/wheels;

EXPOSE 5000
WORKDIR ${LHS_HOME}
VOLUME ["${LHS_HOME}/brains"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gosu", "learninghouse", "tini", "-s", "learninghouse"]
