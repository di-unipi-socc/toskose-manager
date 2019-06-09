ARG PYTHON_VERSION=3.7.2
ARG APP_VERSION

FROM python:${PYTHON_VERSION}-slim as base
ARG APP_VERSION
ENV TOSKOSE_MANAGER_PORT=10000
ENV TOSKOSE_LOGS_PATH=/logs/toskose
ENV TOSKOSE_CONFIG_PATH=/toskose/config
ENV TOSKOSE_MANIFEST_PATH=/toskose/manifest
ENV TOSKOSE_APP_VERSION=${APP_VERSION}

# config dir contains the toskose configuration file
# manifest dir contains the TOSCA manifest file
RUN mkdir -p /toskose/config /toskose/manifest ${TOSKOSE_LOGS_PATH}

WORKDIR /toskose/source
COPY . .

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
    dnsutils \
    > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && python -m ensurepip \
    && pip install --no-cache-dir -r requirements.txt \
    && chmod +x entrypoint.sh

ENTRYPOINT ["/bin/bash", "-c", "/toskose/source/entrypoint.sh"]

FROM base as release
    