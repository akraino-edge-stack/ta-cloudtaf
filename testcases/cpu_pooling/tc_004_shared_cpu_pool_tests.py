import sys
import os
import time
import yaml
import common_utils
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from datetime import datetime
from datetime import timedelta
from decorators_for_robot_functionalities import *
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

ex = BuiltIn().get_library_instance('execute_command')
cpupools = {}
max_shared_pool_size = 0


def tc_004_shared_cpu_pool_tests():
    steps = [
        'step1_shared_passed',
        'step2_shared_fail'
    ]

    BuiltIn().run_keyword("tc_004_shared_cpu_pool_tests.Setup")
    common_utils.keyword_runner(steps)


def Setup():
    global cpupools, max_shared_pool_size, nodename
    nodename = common_utils.decide_nodename()
    cpupools = common_utils.get_cpupools()
    logger.info("CPU pools: " + str(cpupools))
    max_shared_pool_size = get_max_shared_cpus_len()


def step1_shared_passed():
    cpu_request = 500
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-shared1", release_name="cpu-pooling",
                                  values="registry_url={url},pool_req={cpu_req},"
                                         "nodename={node_name}".format(url=reg, cpu_req=cpu_request,
                                                                       node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod4,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        test_pod_cpu_usage(cpu_pooling_pod4['obj_name'], 90, cpu_request)
        check_cpu_resources(cpu_pooling_pod4['obj_name'])

    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod4,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


def step2_shared_fail():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-shared1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},pool_req={cpus},nodename={node_name}"
                                  .format(reg_url=reg, cpus=(max_shared_pool_size*1000)+100, node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod4,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=90,
                                                    delay=3)
        ex.execute_unix_command('kubectl describe pod {podname} | grep "{check_str}"'
                                .format(podname=cpu_pooling_pod4['obj_name'],
                                        check_str='Insufficient nokia.k8s.io/shared_caas'))
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod4,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@robot_log
def test_pod_cpu_usage(pod_name, timeout, threshold):
    command = "kubectl top pod `kubectl get pod | grep {name} | awk '{{print $1}}'`".format(name=pod_name)
    result, ec = ex.execute_unix_command(command, fail_on_non_zero_rc=False)
    logger.info(ec + " - " + result)
    wait_until = datetime.now() + timedelta(seconds=timeout)
    while (ec != "0" or "0m" in result) and (datetime.now() < wait_until):
        result, ec = ex.execute_unix_command(command, fail_on_non_zero_rc=False)
        logger.info(ec + " - " + result)
        time.sleep(1)
    if ec != "0":
        raise Exception("test_pod_cpu_usage failed: " + result)
    else:
        result = result.splitlines()[1].split()[1]
    if int(result[:-1]) < threshold - 10 or int(result[:-1]) > threshold + 10:
        raise Exception("CPU usage: {0} - request: {1}m".format(result, threshold))


def get_max_shared_cpus_len():
    maxlen = 0
    for node in cpupools:
        if 'shared_caas' in cpupools[node].keys() and len(cpupools[node]['shared_caas']) > maxlen:
            maxlen = len(cpupools[node]['shared_caas'])
    return maxlen


@robot_log
def check_cpu_resources(pod_name):
    command = "kubectl get pod `kubectl get pod | grep {name} | awk '{{print $1}}'` -o yaml".format(name=pod_name)
    result = ex.execute_unix_command(command)
    result_dict = yaml.safe_load(result)
    resources = result_dict['spec']['containers'][0]['resources']
    if resources['requests']['cpu'] != '0':
        raise Exception("CPU request should be 0! CPU request: " + resources['requests']['cpu'])
    if resources['limits']['cpu'][:-1] != resources['limits']['nokia.k8s.io/shared_caas']:
        raise Exception("CPU limit should be equal to nokia.k8s.io/shared_caas! " + resources['requests']['cpu'])
