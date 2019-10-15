#!/bin/bash -ex
env_file="$1"

echo ">> dockerlogin"

export WORKDIR=/cloudtaf
source ${WORKSPACE}/resources/scripts/include/DockerFunctions
if [[ -v JENKINS_CONTAINERIZED ]] && [ "${JENKINS_CONTAINERIZED}" == "true" ] 
then
  export RESULT_FOLDER_ON_HOST=/root/jenkins_ws/workspace/$(basename "${WORKSPACE}")
else
  export RESULT_FOLDER_ON_HOST=${WORKSPACE}
fi

source ${WORKSPACE}/resources/scripts/include/version.sh
dockerlogin
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
  -e SKIP_BM_ONBOARD=${SKIP_BM_ONBOARD} \
  -e ${WORKDIR}=${WORKDIR} \
  -v ${WORKSPACE}:${WORKDIR} \
  -w ${WORKDIR} \
  ${ARTY_URL}/tools/robot:${ROBOT_VERSION}

echo ">> Done"
