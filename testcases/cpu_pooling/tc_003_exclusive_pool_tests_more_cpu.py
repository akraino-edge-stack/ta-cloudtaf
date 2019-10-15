import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
import common_utils
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from decorators_for_robot_functionalities import *
from test_constants import *


ex = BuiltIn().get_library_instance('execute_command')
cpupools = {}


def tc_003_exclusive_pool_tests_more_cpu():
    steps = ['step1_with_two_process']
    BuiltIn().run_keyword("tc_003_exclusive_pool_tests_more_cpu.Setup")
    common_utils.keyword_runner(steps)


def Setup():
    global cpupools, nodename
    nodename = common_utils.decide_nodename()
    cpupools = common_utils.get_cpupools()
    logger.info("CPU pools: " + str(cpupools))
    logger.info("Default nodename to deploy: " + nodename)


def step1_with_two_process():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive3", release_name="cpu-pooling",
                                  values="registry_url=" + reg + ",nodename=" + nodename)
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod3,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=10)

        exclusive_cpus = cpupools[nodename]['exclusive_caas']

        proc1_cpu, proc2_cpu = get_cpu_core_of_processes(cpu_pooling_pod3['obj_name'], "dumb-init -c sleep 1000")
        if proc1_cpu not in exclusive_cpus:
            raise Exception('{pod}: Proc1 running on non exclusive cpu core {cpu}!'
                            .format(pod=cpu_pooling_pod3['obj_name'], cpu=proc1_cpu))
        if proc2_cpu not in exclusive_cpus:
            raise Exception('{pod}: Proc2 running on non exclusive cpu core {cpu}!'
                            .format(pod=cpu_pooling_pod3['obj_name'], cpu=proc2_cpu))
        if proc1_cpu == proc2_cpu:
            raise Exception('{pod}: Two processes use same cpu core: {cpu}!'
                            .format(pod=cpu_pooling_pod3['obj_name'], cpu=proc2_cpu))
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod3,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@robot_log
def get_cpu_core_of_processes(pod_name, command, retry=0):
    cpu_list = []
    exact_pod_name = ex.execute_unix_command("kubectl get pod | grep {0} | awk '{{print $1}}'".format(pod_name))
    bash_command = "ps | grep '{proc_name}' | grep -v grep | awk '{{print $1}}'".format(proc_name=command)
    proc_ids = ex.execute_unix_command("kubectl exec {0} -- {1}".format(exact_pod_name, bash_command))
    logger.info("PROC_IDS:" + proc_ids)
    for id in proc_ids.splitlines():
        bash_command = "cat /proc/{0}/stat | awk '{{print $39}}'".format(id)
        result = ex.execute_unix_command("kubectl exec `kubectl get pod | grep {0} | awk '{{print $1}}'` -- {1}".format(pod_name, bash_command))
        logger.info("CPU for pid " + id + "is: " + result)
        cpu_list.append(int(result))
    retry = retry + 1
    if len(cpu_list) == 1:
        return cpu_list[0]
    elif len(cpu_list) == 0:
        return get_cpu_core_of_processes(cpu_pooling_pod3['obj_name'], "dumb-init -c sleep 1000", retry) if retry < 6 else ""
    else:
        return cpu_list
