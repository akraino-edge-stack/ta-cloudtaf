#!/bin/bash -ex

env_file=${1:-include/robot_container.env}
source ${env_file}

yes | cp -rf ../../libraries/ ${ROBOT_CONTAINER_PATH}
yes | cp -rf ../../testcases/ ${ROBOT_CONTAINER_PATH}

docker build --network=host --no-cache --build-arg HTTP_PROXY="${http_proxy}" --build-arg HTTPS_PROXY="${https_proxy}" --build-arg NO_PROXY="${no_proxy}" --build-arg http_proxy="${http_proxy}" --build-arg https_proxy="${https_proxy}" --build-arg no_proxy="${no_proxy}" --tag ${ROBOT_CONTAINER_TAG} ${ROBOT_CONTAINER_PATH}

rm -rf ${ROBOT_CONTAINER_PATH}/libraries/ ${ROBOT_CONTAINER_PATH}/testcases/
  
echo ">> Done"
