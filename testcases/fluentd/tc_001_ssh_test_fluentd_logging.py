import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../common'))

from robot.libraries.BuiltIn import BuiltIn
from decorators_for_robot_functionalities import *
import common_utils
from robot.api import logger
from test_constants import *

ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
log_dir = os.path.join(os.path.dirname(__file__))


def tc_001_ssh_test_fluentd_logging():
    steps = ['step1_fluentd_logging_followup_check']
    common_utils.keyword_runner(steps)


# Get all pods or list of pods running on a node
def kubernetes_get_all_pods(node, podsList):
    pods = []
    for po in podsList:
        command = "kubectl get po --all-namespaces -o wide | grep " + node + " | grep -vP '"
        for pod in pods_skipped[:-1]:
            command += pod + '|'
        command += pods_skipped[-1] + "' | grep " + po + " | awk '{print $2}'"
        stdout = ex.execute_unix_command_on_remote_as_root(command, node)
        for line in stdout.splitlines():
            pods.append(line)
    logger.info(pods)
    return pods


# Check wether logs from pods are gathered by fluentd or not
# - Logs from pods in kube-system are monitored
# - Logs from glusterfs in default are monitored
# Looking into fluentd logs for messages like below:
# "2017-10-17 13:03:14 +0000 [info]: plugin/in_tail.rb:586:initialize: following tail of
# /var/log/containers/kube-proxy-172.24.16.104_kube-system_kube-proxy-
# 81ea7d0e0fcfd372ac3cc2a7f980dc7761ede68566b1ef30663cbb1e46307e62.log"
# meaning that e.g. kube-proxy container log is managed by fluentd
# The research starts from the first "fluent starting" message and stops at first "restarting" occurrence if any
def fluentd_logging_followup_check(nodes, followedPods):
    for key in nodes:
        command = "kubectl get po --all-namespaces -o wide|grep " + nodes[key] + "|grep fluent|awk '{print $2}'"
        fluentd = ex.execute_unix_command(command)
        pods = kubernetes_get_all_pods(nodes[key], followedPods)
        if fluentd is not None:
            for pod in pods:
                command = "kubectl -n kube-system logs " + fluentd + \
                          "|awk '/starting fluentd/{p=1;next}/restarting/{exit} p'|grep -c 'following.*'" + pod
                logger.info(command)
                stdout = ex.execute_unix_command_on_remote_as_root(command, nodes[key])
                if stdout[0] == '0':
                    err = key + ": Pod not followed by fluentd: " + pod
                    raise Exception(err)
        else:
            err = key + ": Fluentd pod not found"
            raise Exception(err)


@Pabot_lock("cpu_pooling")
def step1_fluentd_logging_followup_check():
    logger.console("\nstep1_fluentd_logging_followup_check")

    nodes = stack_infos.get_crf_nodes()
    # Monitor all pods in kube-system namespace
    podsList = ["kube-system"]
    fluentd_logging_followup_check(nodes, podsList)

    nodes = stack_infos.get_storage_nodes()
    # Monitor all pods in kube-system namespace
    podsList = ["kube-system"]
    fluentd_logging_followup_check(nodes, podsList)

    nodes = stack_infos.get_worker_nodes()
    # Monitor all pods in kube-system namespace
    podsList = ["kube-system"]
    fluentd_logging_followup_check(nodes, podsList)
