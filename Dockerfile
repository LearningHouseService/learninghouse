FROM python:3.8 

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.docker.dockerfile="/Dockerfile" \
    org.label-schema.license="MIT" \
    org.label-schema.name="learningHouse" \
    org.label-schema.vendor="learningHouse Service Maintainer" \
    org.label-schema.version=$VERSION \
    org.label-schema.description="learningHouse provides machine learning algorithms based on scikit-learn python library as a RESTful API, with the purpose to give smart home fans an easy possibility to teach their homes." \
    org.label-schema.url="https://github.com/LearningHouseService" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-type="Git" \
    org.label-schema.vcs-url="https://github.com/LearningHouseService/learninghouse-docker.git" \
    maintainer="Johannes Ott <info@johannes-ott.net>"

ENV LHS_HOME=/learninghouse \
    USER_ID=9002 \
    GROUP_ID=9002 \
    HOST=0.0.0.0 \
    PORT=5000 \
    VERBOSITY_LEVEL=INFO

COPY entrypoint.sh /
COPY start.sh ${LHS_HOME}/start.sh

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
