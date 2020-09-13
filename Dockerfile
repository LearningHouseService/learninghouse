FROM python:3.8 

MAINTAINER Johannes Ott <info@johannes-ott.net>

ENV LHS_HOME=/learninghouse \
    USER_ID=9002 \
    GROUP_ID=9002 

COPY entrypoint.sh /
COPY start.sh ${LHS_HOME}/start.sh

ARG VERSION

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        gosu \
        tini && \
    ln -s -f $(which gosu) /usr/local/bin/gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && \
    mkdir -p ${LHS_HOME} && \
    mkdir -p ${LHS_HOME}/models/config && \
    mkdir -p ${LHS_HOME}/models/training && \
    mkdir -p ${LHS_HOME}/models/compiled && \
    cd ${LHS_HOME} && \
    pip3 install learninghouse==${VERSION} && \
    chmod +x /entrypoint.sh ${LHS_HOME}/start.sh

EXPOSE 5000
WORKDIR ${LHS_HOME}
VOLUME ["${LHS_HOME}/models"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gosu", "learninghouse", "tini", "-s", "./start.sh"]
