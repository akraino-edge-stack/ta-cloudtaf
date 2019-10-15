#!/bin/bash -ex

env_file=${1:-include/robot_container.env}
source ${env_file}
ROBOT_CONTAINER_PATH=../robot_container/

yes | cp -rf ../../libraries/ ${ROBOT_CONTAINER_PATH}
yes | cp -rf ../../testcases/ ${ROBOT_CONTAINER_PATH}
mkdir -p ${ROBOT_CONTAINER_PATH}resources/
yes | cp -rf ../../resources/scripts/ ${ROBOT_CONTAINER_PATH}resources/
yes | cp -rf ../../resources/test_charts/ ${ROBOT_CONTAINER_PATH}resources/
yes | cp -rf ../../resources/test_containers/ ${ROBOT_CONTAINER_PATH}resources/

docker build --network=host --no-cache --build-arg HTTP_PROXY="${http_proxy}" --build-arg HTTPS_PROXY="${https_proxy}" --build-arg NO_PROXY="${no_proxy}" --build-arg http_proxy="${http_proxy}" --build-arg https_proxy="${https_proxy}" --build-arg no_proxy="${no_proxy}" --tag ${ROBOT_CONTAINER_TAG} ${ROBOT_CONTAINER_PATH}

rm -rf ${ROBOT_CONTAINER_PATH}/libraries/ ${ROBOT_CONTAINER_PATH}/testcases/ ${ROBOT_CONTAINER_PATH}/resources/
  
echo ">> Done"
