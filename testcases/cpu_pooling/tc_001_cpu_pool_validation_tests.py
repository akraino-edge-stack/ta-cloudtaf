import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
import re
import common_utils
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from decorators_for_robot_functionalities import *
from time import sleep
from test_constants import *


ex = BuiltIn().get_library_instance('execute_command')
cpupools = {}


def tc_001_cpu_pool_validation_tests():
    steps = [
        'step1_check_default_pool_cpu_node_capacity',
        'step2_exclusive_and_shared',
        'step3_annotation_without_requests',
        'step4_annotation_without_container',
        'step5_annotation_without_cpus',
        'step6_request_for_default_pool',
        'step7_pod_use_default_pool_guaranteed',
        'step8_pod_use_default_pool_burstable',
        'step9_1_exclusive_1_shared',
        'step10_cpu_allowed_list_set_after_test_pod_deployed'
    ]
    BuiltIn().run_keyword("tc_001_cpu_pool_validation_tests.Setup")
    common_utils.keyword_runner(steps)


@pabot_lock("flannel_ip")
def Setup():
    global cpupools, nodename
    nodename = common_utils.decide_nodename()
    cpupools = common_utils.get_cpupools()
    logger.info("CPU pools: " + str(cpupools))
    logger.info("Default nodename to deploy: " + nodename)


# set lock to not run with HPA_checks tests
@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step1_check_default_pool_cpu_node_capacity():
    node_cpu_capacity = get_node_cpu_capacity(nodename)
    cpu_request = "{0}m".format(node_cpu_capacity)
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-default1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name},cpu_request={cpu},cpu_limit={cpu}"
                                  .format(reg_url=reg, node_name=nodename, cpu=cpu_request))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod7,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)
        logger.info("Default pool allocation successfull with maximum allocatable cpus!")
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod7,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)

        cpu_request = "{0}m".format(node_cpu_capacity + 10)
        common_utils.helm_install(chart_name="default/cpu-pooling-default1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name},cpu_request={cpu},cpu_limit={cpu}"
                                  .format(reg_url=reg, node_name=nodename, cpu=cpu_request))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod7,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=90,
                                                    delay=3)
        logger.info("Default pool allocation failed with more cpu than allocatable as expected!")
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod7,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step2_exclusive_and_shared():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-mix2", release_name="cpu-pooling",
                                  values="registry_url={reg_url}".format(reg_url=reg))

        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod6,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)
        allowed_cpu_for_pod = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod6['obj_name'])
        requested_cpupool = cpupools[nodename]['exclusive_caas'] + cpupools[nodename]['shared_caas']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpu_for_pod, requested_cpupool):
            raise Exception('{pod} not allocate CPUs from {req_pool} pool!'.format(pod=cpu_pooling_pod6['obj_name'],
                                                                                   req_pool=requested_cpupool))
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod6,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step3_annotation_without_requests():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-annotation1", release_name="cpu-pooling",
                                  values="registry_url={reg_url}".format(reg_url=reg))
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod9,
                                             tester_function=common_utils.test_kubernetes_object_available,
                                             timeout=30,
                                             delay=3)

        result = ex.execute_unix_command('kubectl describe replicasets {0}'.format(cpu_pooling_pod9['obj_name']))

        error = 'Container cpu-pooling has no pool requests in pod spec'

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod9,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step4_annotation_without_container():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-annotation2", release_name="cpu-pooling",
                                  values="registry_url={reg_url}".format(reg_url=reg))
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod10,
                                             tester_function=common_utils.test_kubernetes_object_available,
                                             timeout=30,
                                             delay=3)

        result = ex.execute_unix_command('kubectl describe replicasets {0}'.format(cpu_pooling_pod10['obj_name']))

        error = "'container' is mandatory in annotation"

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod10,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step5_annotation_without_cpus():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-annotation3", release_name="cpu-pooling",
                                  values="registry_url={reg_url}".format(reg_url=reg))
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod11,
                                             tester_function=common_utils.test_kubernetes_object_available,
                                             timeout=30,
                                             delay=3)

        result = ex.execute_unix_command('kubectl describe replicasets {0}'.format(cpu_pooling_pod11['obj_name']))

        error = "'cpus' field is mandatory in annotation"

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod11,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("health_check_1")
@pabot_lock("flannel_ip")
def step6_request_for_default_pool():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-default2", release_name="cpu-pooling",
                                  values="registry_url={reg_url}".format(reg_url=reg))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod8,
                                                    expected_result="1",
                                                    filter=r'(Pending)\s*[0]',
                                                    timeout=30,
                                                    delay=3)
        error = "Insufficient nokia.k8s.io/default"
        result = ex.execute_unix_command('kubectl describe pod {podname}'.format(podname=cpu_pooling_pod8['obj_name']))

        if error not in result:
            raise Exception('Replicaset description does not contain expected error! -' + result)
        else:
            logger.info(error)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod8,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("flannel_ip")
def step7_pod_use_default_pool_guaranteed():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-default1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name}".format(reg_url=reg,
                                                                                              node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod7,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        allowed_cpu_for_pod = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod7['obj_name'])
        default_pool = cpupools[nodename]['default']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpu_for_pod, default_pool):
            raise Exception('{pod} not allocate CPU from default pool!'.format(pod=cpu_pooling_pod7['obj_name']))
        check_qos_of_pod(cpu_pooling_pod7['obj_name'], "Guaranteed")
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod7,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("flannel_ip")
def step8_pod_use_default_pool_burstable():
    memory_request = "500Mi"
    cpu_request = "250m"
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-default1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name},mem_request={mem},"
                                         "cpu_request={cpu}".format(reg_url=reg, node_name=nodename, mem=memory_request,
                                                                    cpu=cpu_request))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod7,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        allowed_cpu_for_pod = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod7['obj_name'])
        default_pool = cpupools[nodename]['default']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpu_for_pod, default_pool):
            raise Exception('{pod} not allocate CPU from default pool!'.format(pod=cpu_pooling_pod7['obj_name']))
        check_qos_of_pod(cpu_pooling_pod7['obj_name'], "Burstable")
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod7,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=60)


@pabot_lock("flannel_ip")
def step9_1_exclusive_1_shared():
    try:
        common_utils.helm_install(chart_name="default/cpu-pooling-mix1", release_name="cpu-pooling",
                                  values="registry_url={reg_url},nodename={node_name}".format(reg_url=reg,
                                                                                              node_name=nodename))
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod5,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod5,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)


@pabot_lock("cpu_pooling")
@pabot_lock("flannel_ip")
def step10_cpu_allowed_list_set_after_test_pod_deployed():
    cpu_setter_deleted = False
    try:
        cpu_pooling_setter["obj_count"] = ex.execute_unix_command("kubectl get pod --all-namespaces | "
                                                                  "grep setter | wc -l")
        ex.execute_unix_command("kubectl get ds -n kube-system cpu-setter -o yaml")
        ex.execute_unix_command("kubectl get ds -n kube-system cpu-setter -o yaml > setter.yaml")
        ex.execute_unix_command("kubectl delete ds -n kube-system cpu-setter")

        cpu_setter_deleted = True

        common_utils.check_kubernetes_object(kube_object=cpu_pooling_setter,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)

        common_utils.helm_install(chart_name="default/cpu-pooling-exclusive1", release_name="cpu-pooling",
                                  values="registry_url=" + reg + ",nodename=" + nodename)
        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_pod1,
                                                    expected_result="1",
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)

        allowed_cpus_for_pod_before = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod1['obj_name'])

        ex.execute_unix_command("kubectl create -f setter.yaml")

        common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_setter,
                                                    expected_result=cpu_pooling_setter["obj_count"],
                                                    filter=r'(Running)\s*[0]',
                                                    timeout=90)
        cpu_setter_deleted = False
        allowed_cpus_for_pod_after = common_utils.get_cpu_allowed_list_from_pod(cpu_pooling_pod1['obj_name'])
        exclusive_cpus = cpupools[nodename]['exclusive_caas']
        if not common_utils.allowed_cpus_is_in_cpu_pool(allowed_cpus_for_pod_after, exclusive_cpus):
            raise Exception('{pod} not allocate CPU from exclusive pool!'.format(pod=cpu_pooling_pod1['obj_name']))
        if set(allowed_cpus_for_pod_before) == set(allowed_cpus_for_pod_after):
            raise Exception('Allocated CPUs before setter deployed is equal with CPU set after deploy!')
    finally:
        common_utils.helm_delete("cpu-pooling")
        common_utils.check_kubernetes_object(kube_object=cpu_pooling_pod1,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=90)
        setter_count = ex.execute_unix_command("kubectl get pod --all-namespaces | grep setter | wc -l")
        if cpu_setter_deleted:
            if setter_count != "0":
                search_cmd = "kubectl get pod -n kube-system |grep setter | awk '{print $1}'"
                del_cmd = "kubectl -n kube-system delete pod --grace-period=0 --force --wait=false"

                ex.execute_unix_command("for i in `{search}`; do {delete} $i; done".format(search=search_cmd,
                                                                                           delete=del_cmd))
                common_utils.check_kubernetes_object(kube_object=cpu_pooling_setter,
                                                     tester_function=common_utils.test_kubernetes_object_not_available,
                                                     timeout=90)
            ex.execute_unix_command("kubectl create -f setter.yaml")

            common_utils.test_kubernetes_object_quality(kube_object=cpu_pooling_setter,
                                                        expected_result=cpu_pooling_setter["obj_count"],
                                                        filter=r'(Running)\s*[0]',
                                                        timeout=90)


@robot_log
def check_qos_of_pod(podname, qos_type):
    command = "kubectl describe pod " \
              "`kubectl get pod | grep {0} | awk '{{print $1}}'` | grep 'QoS Class:'".format(podname)
    result = ex.execute_unix_command(command)
    if qos_type not in result:
        raise Exception("{pod} QoS should be {qos}, instead of {result}!".format(pod=podname, qos=qos_type,
                                                                                 result=result))


@robot_log
def get_node_cpu_capacity(node_name):
    command = "kubectl describe node `kubectl get no -L=nodename | grep {nodename} | awk '{{print $1}}'`"\
        .format(nodename=node_name)
    result = ex.execute_unix_command(command)
    matched = re.search(r'Allocatable:(.|\n)*cpu:\s+(\d+)', result)
    if matched:
        max_cap = int(matched.group(2)) * 1000
        matched = re.search(r'cpu\s+(\d+)m', result)
        if matched:
            return max_cap - int(matched.group(1))
    raise Exception('Failed getting node CPU capacity!')
