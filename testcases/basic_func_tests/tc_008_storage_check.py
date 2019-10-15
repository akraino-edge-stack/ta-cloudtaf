import sys
import os
import time

from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
from decorators_for_robot_functionalities import *
import common_utils
from test_constants import *
BuiltIn().import_library('pabot.PabotLib')
pabot = BuiltIn().get_library_instance('pabot.PabotLib')

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
pv_name = ""

def tc_008_storage_check():
    steps = ['step1_read_write_pv',
             'step2_check_pv_retaining',
             'step3_read_write_pv',
             ]
    BuiltIn().run_keyword("tc_008_storage_check.Setup")
    common_utils.keyword_runner(steps)

def Setup():
    pabot.acquire_lock("pv_test_ip")
    common_utils.wait_if_pressure()
    install_charts()

def step1_read_write_pv():
    read_write_pv("step1.log")


@Pabot_lock("health_check_2")
def step2_check_pv_retaining():
    common_utils.helm_delete("storage-test")
    common_utils.check_kubernetes_object(kube_object=pv_test_pod,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=90)
    _install_storage_test_helm_chart()
    pabot.release_lock("pv_test_ip")

def step3_read_write_pv():
    read_write_pv("step3.log")

def read_write_pv(file_name):
    pod_list = execute.execute_unix_command("kubectl get pod | grep pv-test-deployment | grep -i running | awk '{print $1}'")

    # write log on persistent storage from pods
    for pod in pod_list.split("\n"):
        pod = pod.strip()
        logger.info("POD NAME: " + pod)
        execute.execute_unix_command(
            "kubectl exec " + pod + " -- sh -c 'echo test_log_" + pod + " >> /usr/share/storage_test/" + file_name + "'")

    # check if logs can be reached from containers
    for pod in pod_list.split("\n"):
        pod = pod.strip()
        log = execute.execute_unix_command(
            "kubectl exec " + pod + " -- sh -c 'cat /usr/share/storage_test/" + file_name + "'")
        for pod in pod_list.split("\n"):
            pod = pod.strip()
            if pod not in log:
                raise Exception("Log entry: test_log_" + pod + " is not found in log file")

@Pabot_lock("health_check_2")
def install_charts():
    common_utils.helm_install(chart_name="default/persistentvolume-claim", release_name="pvc")
    common_utils.wait_if_pressure()
    common_utils.check_kubernetes_object(kube_object=pv_test_pvc,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Bound", timeout=90)
    _install_storage_test_helm_chart()

    global pv_name
    pv_name = execute.execute_unix_command("kubectl get pvc | grep pvc- | awk {'print$3'}")


def _install_storage_test_helm_chart():
    if stack_infos.get_worker_nodes():
        common_utils.helm_install(chart_name="default/storage-test-worker", release_name="storage-test")
    else:
        common_utils.helm_install(chart_name="default/storage-test-oam", release_name="storage-test")
    common_utils.wait_if_pressure()
    common_utils.check_kubernetes_object(kube_object=pv_test_pod,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Running", timeout=60)
