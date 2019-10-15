#!/bin/bash -xe

function execute_test_suites {
  IP="$1"
  suite_count=`ls ${WORKDIR}/testcases/parallel_suites/ | grep -c .robot`
  set +e
  mkdir -p ~/.ssh
  touch ~/.ssh/known_hosts
  ssh-keygen -R ${SUT_IP} -f ~/.ssh/known_hosts
  PABOT_PORT=$((20000 + ${BUILD_NUMBER}))
  pabot --verbose --processes ${suite_count} --pabotlib --pabotlibport ${PABOT_PORT} -d ${WORKDIR}/pabot_logs/ -i ${TC_TAG}AND${ENV} --variable floating_ip:${SUT_IP} --loglevel trace ${WORKDIR}/testcases/parallel_suites

  set -e
}

function replace_password
  if [[ -n "${PASSWORD}" ]] && [[ ${PASSWORD} != "adminpass" ]]
  then
    sed -i "s|cloudadmin = {'username': 'cloudadmin', 'password': 'adminpass'}|cloudadmin = {'username': 'cloudadmin', 'password': '${PASSWORD}'}|g" ${WORKDIR}/libraries/common/users.py
    fi

. ${WORKDIR}/resources/scripts/include/crf-registry
if [[ -n "${SKIP_BM_ONBOARD}" ]] && [[ "${SKIP_BM_ONBOARD}" != "true" ]]
then
  ${WORKDIR}/resources/scripts/prepare_robot_bm.py
fi

replace_password
execute_test_suites ${SUT_IP}
echo "end of robot-deployment-test.sh script"

exit 0
