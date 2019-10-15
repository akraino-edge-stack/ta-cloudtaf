import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

from robot.libraries.BuiltIn import BuiltIn
from decorators_for_robot_functionalities import *
import common_utils
from robot.api import logger
from test_constants import *


ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
log_dir = os.path.join(os.path.dirname(__file__))


def tc_002_pod_health_check():
    steps = ['step1_check_componentstatus',
             'step2_check_kubelet_is_running',
             'step3_check_apiserver_is_running',
             'step4_check_all_kubernetes_pod',
             'step5_check_services_with_systemctl']
    common_utils.keyword_runner(steps)


@Pabot_lock("health_check_1")
@Pabot_lock("health_check_2")
def step1_check_componentstatus():
    stdout = ex.execute_unix_command("kubectl get componentstatus -o json | jq .items[].conditions[].type")
    logger.console('\n')
    for line in stdout.split('\n'):
        if "Healthy" in line:
            logger.console(line)
        else:
            raise Exception(line)


@Robot_log
def check_container_is_running(name, nodes):
    for key in nodes:
        stdout = ex.execute_unix_command_on_remote_as_user("docker ps --filter status=running --filter name=" + name + " | grep -v pause | grep " + name + " | wc -l ", nodes[key])
        if stdout == '1':
            logger.console("\n" + name + " container is running on node " + key + ".")
        else:
            stdout = ex.execute_unix_command_on_remote_as_user("docker ps | grep -v pause | grep " + name, nodes[key])
            raise Exception(name + "container is NOT running on node " + key + "\n" + stdout)


@Robot_log
def check_program_is_running(name, nodes):
    for key in nodes:
        stdout = ex.execute_unix_command_on_remote_as_user("ps -aux | grep '" + name + "' | grep -v 'color' | wc -l ", nodes[key])
        if stdout == '1':
            logger.console("\n" + name + " is running on node " + key + ".")
        else:
            stdout = ex.execute_unix_command_on_remote_as_user("ps -aux | grep '" + name + "' | grep -v 'color'" , nodes[key])
            raise Exception(name + " is NOT running on node " + key + "\n" + stdout)


def step2_check_kubelet_is_running():
    all_nodes = stack_infos.get_all_nodes()
    check_program_is_running("/kubelet ", all_nodes)
    check_program_is_running("/kubelet_healthcheck.sh", all_nodes)


def step3_check_apiserver_is_running():
    crf_nodes = stack_infos.get_crf_nodes()
    check_container_is_running("kube-apiserver", crf_nodes)

@Pabot_lock("health_check_1")
def step4_check_all_kubernetes_pod():
    log_dir = os.path.join(os.path.dirname(__file__))
    command = "kubectl get po --all-namespaces | tail -n +2 | grep -vP 'Running"
    for pod in pods_skipped:
        command += '|'+pod
    command += "'"
    stdout = ex.execute_unix_command(command, fail_on_non_zero_rc=False, skip_prompt_in_command_output=True)[0]
    if not stdout:
        logger.console("\nAll kubernetes PODs are running.")
        return
    for line in stdout.split("\n"):
        line = line.split()
        command = "kubectl logs --namespace " + line[0] + " " + line[1]
        filename = "tc004_step1_" + line[1] + ".log"
        common_utils.gather_logs(command, filename, log_dir)
    raise Exception(stdout)


def step5_check_services_with_systemctl():
    all_nodes = stack_infos.get_all_nodes()
    command = "systemctl status | grep -E 'State: running|Jobs: 0 queued|Failed: 0 units' | grep -v grep"
    for key in all_nodes:
        logger.console(key)
        stdout = "\nsystemctl status output:\n" + ex.execute_unix_command_on_remote_as_user(command, all_nodes[key])
        if all(x in stdout for x in ["State: running", "Jobs: 0 queued", "Failed: 0 units"]):
            logger.console(stdout)
        else:
            #cat is needed here to remove the coloring of the systemctl for the robot logs
            failedservices = ex.execute_unix_command_on_remote_as_user("systemctl --failed | cat", all_nodes[key])
            # TODO: cloud-final.service fails with unknown reason
            if any(service in failedservices for service in services_skipped):
                stdout = stdout + "\n" + ex.execute_unix_command_on_remote_as_user("systemctl --failed | cat", all_nodes[key])
                logger.console(stdout)
            else:
                stdout = stdout + "\n" + ex.execute_unix_command_on_remote_as_user("systemctl --failed | cat", all_nodes[key])
                raise Exception(stdout)
