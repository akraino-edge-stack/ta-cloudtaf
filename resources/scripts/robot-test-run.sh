#!/bin/bash -ex
env_file=${1:-include/robot_container.env}

source ${env_file}
#source ${WORKSPACE}/resources/scripts/include/version.sh

echo ">> Run robot-container"
docker run \
  -i \
  --rm \
  --net=host \
  --pid=host \
  --name robot-test-${BUILD_NUMBER} \
  -e ENV=${ENV} \
  -e TC_TAG=${TC_TAG} \
  -e SUT_IP=${SUT_IP} \
  -e ARTY_LOGIN=${ARTY_LOGIN} \
  -e ARTY_PASS=${ARTY_PASS} \
  -e ARTY_PASS_HASH=${ARTY_PASS_HASH} \
  -e ARTY_REPO_URL=${ARTY_REPO_URL} \
  -e ARTY_APP_IMAGE_DIR=${ARTY_APP_IMAGE_DIR} \
  -e APP_IMAGE_URL=${APP_IMAGE_URL} \
  -e BUILD_NUMBER=${BUILD_NUMBER} \
  -e PASSWORD=${PASSWORD} \
  -e SKIP_BM_ONBOARD=${SKIP_BM_ONBOARD} \
  -e WORKDIR=${WORKDIR} \
  -v ${WORKSPACE}:${WORKDIR} \
  -w ${WORKDIR} \
  ${ROBOT_CONTAINER_TAG}

echo ">> Done"
