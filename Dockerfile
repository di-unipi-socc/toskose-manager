ARG PYTHON_VERSION=3.7.2

FROM python:${PYTHON_VERSION}-slim as base
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.name="Toskose Manager" \
      org.label-schema.description="The orchestrator of Toskose" \
      org.label-schema.vcs-url="https://github.com/di-unipi-socc/toskose-manager" \
      org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.vendor="SOCC Unipi" \
      org.label-schema.version=${VERSION} \
      org.label-schema.schema-version="1.0"

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