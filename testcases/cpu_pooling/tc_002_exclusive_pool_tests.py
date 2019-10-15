import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
import common_utils
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from decorators_for_robot_functionalities import *
from time import sleep
from test_constants import *


ex = BuiltIn().get_library_instance('execute_command')
cpupools = {}


def tc_002_exclusive_pool_tests():
    steps = [
        'step1_no_annotation',
        'step2_with_annotation',
        'step3_more_replicas_than_cpus',
        'step4_request_more_than_cpus',
        'step5_less_cpu_annotation_than_request',
        'step6_more_cpu_annotation_than_request',
        'step_7_allocate_all_exclusive_and_new_one_start_running_after_needed_resource_is_freed_up'
    ]

    BuiltIn().run_keyword("tc_002_exclusive_pool_tests.Setup")
    common_utils.keyword_runner(steps)


def Setup():
    global cpupools
    global nodename
    nodename = common_utils.decide_nodename()
    cpupools = common_utils.get_cpupools()
    logger.info("CPU pools: " + str(cpupools))
    logger.info("Default nodename to deploy: " + nodename)


@pabot_lock("flannel_ip")
def step1_no_annotation():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name}".format(reg_url=reg,
                                                                                              node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod1,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        allowed_cpu_for_pod = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod1['obj_name'])
        exclusive_cpus = cpupools[nodename]['exclusive_caas']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpu_for_pod, exclusive_cpus):
            raise Exception('{pod} not allocate CPU from exclusive pool!'.format(pod=cpu_pooling_pod1['obj_name']))
    except Exception as e:
        raise e
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod1,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("flannel_ip")
def step2_with_annotation():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name}".format(reg_url=reg,
                                                                                              node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod2,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        allowed_cpu_for_pod = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod2['obj_name'])
        exclusive_cpus = cpupools[nodename]['exclusive_caas']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpu_for_pod, exclusive_cpus):
            raise Exception('{pod} not allocate CPU from exclusive pool!'.format(pod=cpu_pooling_pod2['obj_name']))
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("flannel_ip")
def step3_more_replicas_than_cpus():
    num_of_replicas = len(cpupools[nodename]['exclusive_caas'])
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name},replicas={cpus}"
                                  .format(reg_url=reg, cpus=num_of_replicas+1, node_name=nodename))
        cpu_pooling_pod2['obj_count'] = str(num_of_replicas)
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod2,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=90,
                                                    delay=3)
        result = ex.execute_unix_command('kubectl describe pod {podname}'.format(podname=cpu_pooling_pod2['obj_name']))
        error = 'Insufficient nokia.k8s.io/exclusive_caas'

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        cpu_pooling_pod2['obj_count'] = "1"

        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("flannel_ip")
def step4_request_more_than_cpus():
    max_exclusive_pool_size = len(cpupools[nodename]['exclusive_caas'])
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name},proc_req={cpus},pool_req={cpus}"
                                  .format(reg_url=reg, cpus=max_exclusive_pool_size+1, node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod2,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=90,
                                                    delay=3)
        result = ex.execute_unix_command('kubectl describe pod {podname}'.format(podname=cpu_pooling_pod2['obj_name']))
        error = 'Insufficient nokia.k8s.io/exclusive_caas'

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("flannel_ip")
def step5_less_cpu_annotation_than_request():
    annotation_cpu = 1
    request_cpu = 2
    cpu_pooling_pod2['obj_type'] = 'replicaset'
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling",
                                  values="registry_url={url},nodename={node_name},proc_req={proc},pool_req={req}"
                                  .format(url=reg, proc=annotation_cpu, req=request_cpu, node_name=nodename))
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_available,
                                             timeout=10,
                                             delay=3)
        result = ex.execute_unix_command('kubectl describe replicaset {0}'.format(cpu_pooling_pod2['obj_name']))
        error = 'Exclusive CPU requests {req} do not match to annotation {proc}'.format(req=request_cpu,
                                                                                        proc=annotation_cpu)

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)
        cpu_pooling_pod2['obj_type'] = 'pod'


@pabot_lock("flannel_ip")
def step6_more_cpu_annotation_than_request():
    annotation_cpu = 2
    request_cpu = 1
    cpu_pooling_pod2['obj_type'] = 'replicaset'
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling",
                                  values="registry_url={url},nodename={node_name},proc_req={proc},pool_req={req}"
                                  .format(url=reg, proc=annotation_cpu, req=request_cpu, node_name=nodename))
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_available,
                                             timeout=10,
                                             delay=3)
        result = ex.execute_unix_command('kubectl describe replicaset {0}'.format(cpu_pooling_pod2['obj_name']))
        error = 'Exclusive CPU requests {req} do not match to annotation {proc}'.format(req=request_cpu,
                                                                                        proc=annotation_cpu)

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)
        cpu_pooling_pod2['obj_type'] = 'pod'


@pabot_lock("flannel_ip")
def step_7_allocate_all_exclusive_and_new_one_start_running_after_needed_resource_is_freed_up():
    max_exclusive_pool_size = len(cpupools[nodename]['exclusive_caas'])
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive2", release_name="cpu-pooling1",
                                  values="registry_url={reg_url},nodename={node_name},proc_req={cpus},pool_req={cpus}"
                                  .format(reg_url=reg, cpus=max_exclusive_pool_size, node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod2,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)
        logger.info("Allocation of all exclusive CPU successfull!")

        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive1", release_name="cpu-pooling2",
                                  values="registry_url={reg_url},nodename={node_name}".format(reg_url=reg,
                                                                                              node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod1,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=90,
                                                    delay=3)
        logger.info("Try to allocate more exclusive CPU -> Pod in Pending!")
        common_utils.helm_delete("cpu-pooling1")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod1,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

    finally:
        if common_utils.helm_list("cpu-pooling1") != "0":
            common_utils.helm_delete("cpu-pooling1")
        common_utils.helm_delete("cpu-pooling2")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod1,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod2,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@robot_log
def get_cpu_core_of_process(pod_name, command):
    bash_command = "ps | grep '{proc_name}' | grep -v grep | awk '{{print $1}}'".format(proc_name=command)
    proc_id = ex.execute_unix_command("kubectl exec `kubectl get pod | grep {0} | "
                                      "awk '{{print $1}}'` -- {1}".format(pod_name, bash_command))
    bash_command = "cat /proc/{0}/stat | awk '{{print $39}}'".format(proc_id)
    result = ex.execute_unix_command("kubectl exec `kubectl get pod | grep {0} | "
                                     "awk '{{print $1}}'` -- {1}".format(pod_name, bash_command))
    return int(result)
