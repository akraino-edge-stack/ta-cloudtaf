import sys
import os
import time

from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
from datetime import datetime
from datetime import timedelta
from decorators_for_robot_functionalities import *
from test_constants import *
import common_utils

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')


def Custom_HPA_check():
    steps = ['step1_check_initial_replica_count_custom',
             'step2_check_scale_out_custom',
             'step3_check_scale_in_custom']
    BuiltIn().run_keyword("Custom_HPA_check.setup")
    common_utils.keyword_runner(steps)


get_pod_replica_count  = "kubectl get hpa --namespace=kube-system | grep podinfo | awk '{print $6}'"

def setup():
    #flags = ["--horizontal-pod-autoscaler-downscale-stabilization=10s", "--horizontal-pod-autoscaler-sync-period=10s"]
    #common_utils.modify_static_pod_config(common_utils.add_flag_to_command, "cm.yml", flags)
    common_utils.helm_install(chart_name="default/custom-metrics", release_name="podinfo")
    common_utils.check_kubernetes_object(kube_object=podinfo_pod,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Running",
                                         timeout=90)

def step1_check_initial_replica_count_custom():
    expected_initial_replica_num = 2
    timeout = 1000
    check_scaling(expected_initial_replica_num, timeout)

def step2_check_scale_out_custom():
    common_utils.helm_install(chart_name="default/http-traffic-gen", release_name="http-traffic-gen")
    common_utils.check_kubernetes_object(kube_object=http_traffic_gen,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Running",
                                         timeout=45)
    expected_replicas = 3
    timeout = 1000
    check_scaling(expected_replicas, timeout)

def step3_check_scale_in_custom():
    expected_replicas = 2
    timeout = 1000
    check_scaling(expected_replicas, timeout)

def check_scaling(expected_replicas, timeout=60):
    i = 0
    for i in range(timeout):
        BuiltIn().sleep('1s')
        actual_replicas = int(
                              execute.execute_unix_command(get_pod_replica_count))
        if actual_replicas == expected_replicas:
            break
    BuiltIn().should_be_equal(actual_replicas, expected_replicas)
