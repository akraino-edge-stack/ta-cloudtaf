#!/bin/bash -xe

function execute_test_suites {
  IP="$1"
  suite_count=`ls ${WORKDIR}/testcases/parallel_suites/ | grep -c .robot`
  set +e
  mkdir -p ~/.ssh
  touch ~/.ssh/known_hosts
  ssh-keygen -R ${SUT_IP} -f ~/.ssh/known_hosts
  PABOT_PORT=$((20000 + ${BUILD_NUMBER}))
  pabot --verbose --processes ${suite_count} --pabotlib --pabotlibport ${PABOT_PORT} -d ${WORKDIR} -i ${TC_TAG}AND${ENV} --variable floating_ip:${SUT_IP} --loglevel trace ${WORKDIR}/testcases/parallel_suites

  set -e
}

. ${WORKDIR}/resources/scripts/include/crf-registry
if [[ "${SKIP_BM_ONBOARD}" != "true" ]] && [[ -z "${APP_IMAGE_URL}" ]]
then
  ${WORKDIR}/resources/scripts/prepare_robot_bm.py
elif [[ "${SKIP_BM_ONBOARD}" != "true" ]] && [[ -n "${APP_IMAGE_URL}" ]]
then
  ${WORKDIR}/resources/scripts/prepare_robot_bm.py --app_image_url ${APP_IMAGE_URL}
fi

execute_test_suites ${SUT_IP}
echo "end of robot-deployment-test.sh script"

exit 0
