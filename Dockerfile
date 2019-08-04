ARG PYTHON_VERSION=3.7.2

FROM python:${PYTHON_VERSION}-slim as base
LABEL maintainer.name "Matteo Bogo" \
      maintainer.email "matteo.bogo@protonmail.com"

ENV TOSKOSE_MANAGER_PORT=10000 \
    TOSKOSE_APP_MODE=production \
    TOSKOSE_LOGS_PATH=/logs/toskose \
    TOSKOSE_CONFIG_PATH=/toskose/config \
    TOSKOSE_TOSCA_MANIFEST_PATH=/toskose/manifest

WORKDIR /toskose/source
COPY . .

RUN apt-get update -qq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && mkdir -p /toskose/config /toskose/manifest ${TOSKOSE_LOGS_PATH} \
    && python -m ensurepip \
    && pip install --no-cache-dir -r requirements.txt \
    && chmod +x entrypoint.sh

WORKDIR /toskose
EXPOSE ${TOSKOSE_MANAGER_PORT}/tcp
ENTRYPOINT ["/bin/bash", "-c", "/toskose/source/entrypoint.sh"]    