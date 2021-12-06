FROM python:3.9-slim-buster

ARG VERSION

ENV LHS_HOME=/learninghouse \
    USER_ID=9002 \
    GROUP_ID=9002 \
    LEARNINGHOUSE_HOST=0.0.0.0 \
    LEARNINGHOUSE_PORT=5000

COPY entrypoint.sh /

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        gosu \
        tini && \
    ln -s -f $(which gosu) /usr/local/bin/gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && \
    mkdir -p ${LHS_HOME} && \
    mkdir -p ${LHS_HOME}/brains/config && \
    mkdir -p ${LHS_HOME}/brains/training && \
    mkdir -p ${LHS_HOME}/brains/compiled && \
    cd ${LHS_HOME} && \
    pip3 install learninghouse==${VERSION} && \
    chmod +x /entrypoint.sh

EXPOSE 5000
WORKDIR ${LHS_HOME}
VOLUME ["${LHS_HOME}/brains"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gosu", "learninghouse", "tini", "-s", "learninghouse"]
