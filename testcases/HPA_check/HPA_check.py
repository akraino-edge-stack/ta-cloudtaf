import sys
import os
import time
import common_utils

from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from datetime import datetime
from datetime import timedelta
from decorators_for_robot_functionalities import *
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')


def HPA_check():
    steps = ['step1_check_initial_replica_count',
             'step2_check_scale_out',
             'step3_check_scale_in']
    BuiltIn().run_keyword("HPA_check.setup")
    common_utils.keyword_runner(steps)


def setup():
    common_utils.helm_install(chart_name="default/php-apache", release_name="crf01",
                              values="registry_url={reg_url}".format(reg_url=reg))
    common_utils.check_kubernetes_object(kube_object=php_apache_pod,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Running",
                                         timeout=90)
    flags = ["--horizontal-pod-autoscaler-downscale-stabilization=10s", "--horizontal-pod-autoscaler-sync-period=10s"]
    common_utils.modify_static_pod_config(common_utils.add_flag_to_command, "cm.yml", flags)
    common_utils.helm_install(chart_name="default/load-generator-for-apache", release_name="load")
    common_utils.check_kubernetes_object(kube_object=load_generator_for_apache,
                                         tester_function=common_utils.test_kubernetes_object_available,
                                         additional_filter="Running",
                                         timeout=60)


def step1_check_initial_replica_count():
    time.sleep(5)
    replica_count = int(
        execute.execute_unix_command("kubectl get hpa | grep php-apache-hpa | awk '{print $6}'"))
    if replica_count == 1:
        logger.info("number of php apache pod is 1")
    else:
        raise Exception("Expected initial replica count is not correct: expected: 1, got: " + str(replica_count))


def step2_check_scale_out():
    check_scaling(expected_replicas="2", timeout=360)


def step3_check_scale_in():
    check_scaling(expected_replicas="1", timeout=480)


def check_scaling(expected_replicas, timeout):
    wait_until = datetime.now() + timedelta(seconds=timeout)
    actual_replicas = execute.execute_unix_command("kubectl get hpa | grep php-apache-hpa | awk '{print $6}'")
    while actual_replicas != expected_replicas:
        time.sleep(5)
        actual_replicas = execute.execute_unix_command("kubectl get hpa | grep php-apache-hpa | awk '{print $6}'")
        if actual_replicas == expected_replicas:
            logger.info("number of php apache pod is " + expected_replicas + ", scale out was successful")
        elif wait_until < datetime.now():
            raise Exception("Scaling did not happen in " + str(timeout) + " seconds, expected replica count is " +
                            expected_replicas + ", got " + actual_replicas)
