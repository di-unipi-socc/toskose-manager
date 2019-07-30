# import configuration
# change the case study with the APP_NAME var in deploy.env

dpl ?= deploy.env
include $(dpl)
export $(shell sed 's/=.*//' $(dpl))

.PHONY: validate build deploy undeploy clean
.DEFAULT: build

STACK_FILE=docker-stack-${APP_NAME}.yml

validate:
	docker-compose \
	-f ${STACK_FILE} \
	config \
	--quiet

build:
	docker build \
	-f Dockerfile-dev \
	--build-arg CASE_STUDY=${APP_NAME} \
	--tag ${APP_NAME}-manager:latest \
	--no-cache \
	.

deploy:
	docker stack deploy \
	--compose-file ${STACK_FILE} \
	--orchestrator ${ORCHESTRATOR} \
	${APP_NAME}-stack

undeploy:
	docker stack rm ${APP_NAME}-stack

clean:
	docker rmi ${APP_NAME}-manager:latest --force
	