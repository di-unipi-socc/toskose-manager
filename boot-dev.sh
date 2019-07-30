#!/bin/bash
set -e

# absolute path of current script
ROOT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

DEFAULT_DOCKER_COMPOSE=tests/data/thinking/docker-compose-without-manager.yml
DEFAULT_MANIFEST=tests/data/thinking/config/
DEFAULT_TOSKOSE_CONFIG=tests/data/thinking/manifest/

DEFAULT_LOGS_PATH=$ROOT_DIR/logs/

shutdown () {
    echo "Shutdown."
    docker-compose -f $ROOT_DIR/$DOCKER_COMPOSE down
}

trap ctrl_c INT

function ctrl_c() {
    echo "Detected CTRL-C."
    shutdown
}

if [ ! -f "$DOCKER_COMPOSE" ] || [ ! -d "$MANIFEST" ] || [ ! -d "$TOSKOSE_CONFIG" ]; then
    echo "missing docker-compose file, manifest dir or toskose config dir."
    DOCKER_COMPOSE=$DEFAULT_DOCKER_COMPOSE
    MANIFEST=$DEFAULT_MANIFEST
    TOSKOSE_CONFIG=$DEFAULT_TOSKOSE_CONFIG
    printf "Default application Thinking loaded.\n${DOCKER_COMPOSE}\n${MANIFEST}\n${TOSKOSE_CONFIG}\n"
fi

if [ ! -d "$LOGS_PATH" ]; then
    echo "missing log path, creating one.."
    LOGS_PATH=$DEFAULT_LOGS_PATH
    mkdir -p $LOGS_PATH
fi

if [ ! -d ".venv" ]; then
    echo 'missing virtualenv, creating one..'
    python3 -m venv .venv
fi

# TODO check docker/docker-compose installed?

source .venv/bin/activate
pip install -r requirements.txt

echo "Starting the docker-compose file.."
docker-compose -f $DOCKER_COMPOSE up -d

export TOSKOSE_LOGS_PATH=$LOGS_PATH
export TOSKOSE_APP_MODE=development
export FLASK_ENV=development
export FLASK_APP=run.py

export TOSKOSE_CONFIG_PATH=$TOSKOSE_CONFIG_PATH
export TOSKOSE_MANIFEST_PATH=$MANIFEST

cd app
if ! python -m flask routes; then
    shutdown
fi

if ! python -m flask run; then
    shutdown
fi