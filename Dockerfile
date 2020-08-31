FROM python:3.8 

ENV LHS_HOME=/learninghouse \
    USER_ID=9002 \
    GROUP_ID=9002 

COPY entrypoint.sh /
COPY uwsgi.sh /

ARG VERSION

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        gosu \
        tini && \
    ln -s -f $(which gosu) /usr/local/bin/gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/learninghouse.zip https://github.com/LearningHouseService/learninghouse-core/archive/v$VERSION.zip && \
    cd /tmp && \
    unzip learninghouse.zip && \
    cd learninghouse-core-$VERSION && \
    pip3 install --no-cache-dir -e ./ && \
    cp -r learninghouse ${LHS_HOME} && \
    cp uwsgi.ini ${LHS_HOME}/ && \
    mkdir -p ${LHS_HOME}/models/config && \
    mkdir -p ${LHS_HOME}/models/training && \
    mkdir -p ${LHS_HOME}/models/compiled && \
    chmod +x /entrypoint.sh /uwsgi.sh

EXPOSE 5000

VOLUME ["${LHS_HOME}/models"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gosu", "learninghouse", "tini", "-s", "/uwsgi.sh"]