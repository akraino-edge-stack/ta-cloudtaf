#!/bin/bash -ex
env_file=${1:-include/robot_container.env}

source ${env_file}

export WORKSPACE=$PWD/../../
mkdir -p ${WORKSPACE}/pabot_logs

echo ">> Run robot-container"
docker run \
  -i \
  --rm \
  --net=host \
  --pid=host \
  --name robot-test-${BUILD_NUMBER} \
  -e TC_TAG=${TC_TAG} \
  -e SUT_IP=${SUT_IP} \
  -e BUILD_NUMBER=${BUILD_NUMBER} \
  -e PASSWORD=${PASSWORD} \
  -e SKIP_BM_ONBOARD=${SKIP_BM_ONBOARD} \
  -e WORKDIR=/cloudtaf \
  -v ${WORKSPACE}/pabot_logs:${WORKDIR}/pabot_logs \
  -w ${WORKDIR} \
  ${ROBOT_CONTAINER_TAG}

echo ">> Done"
