import ruamel.yaml
import time
import subprocess
import yaml
import re
import os

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from netaddr import IPAddress
from datetime import datetime
from datetime import timedelta
from decorators_for_robot_functionalities import *
from test_constants import *
from users import *

log_dir = os.path.join(os.path.dirname(__file__))
ex = BuiltIn().get_library_instance('execute_command')
sshlib = ex.get_ssh_library_instance()
stack_infos = BuiltIn().get_library_instance('stack_infos')
BuiltIn().import_library('pabot.PabotLib')
pabot = BuiltIn().get_library_instance('pabot.PabotLib')


def keyword_runner(keywords, counter=0):
    try:
        BuiltIn().run_keyword(keywords[counter])
    except Exception as err:
        raise err
    finally:
        counter += 1
        if len(keywords) > counter:
            keyword_runner(keywords, counter)


@Robot_log
def gather_logs(command, logfile_name, local_path):
    remote_file_path = ROBOT_LOG_PATH + logfile_name
    local_file_path = os.path.join(local_path, logfile_name)
    ex.execute_unix_command_as_root("echo  -e '****** This is the output of: " +
                                    command + " ****** \n' > " + remote_file_path)
    ex.execute_unix_command_as_root(command + " >> " + remote_file_path)
    ex.execute_unix_command_as_root("chmod 777 " + remote_file_path)
    sshlib.get_file(remote_file_path, local_file_path)
    ex.execute_unix_command_as_root("rm -f " + remote_file_path)


@Robot_log
def gather_logs_from_remote(command, logfile_name, local_path, host, user={}):
    if not user:
        user = ex.get_default_user()
    local_file_path = os.path.join(local_path, logfile_name)
    remote_file_path = ROBOT_LOG_PATH + logfile_name
    ex.execute_unix_command_on_remote_as_root("echo  -e '****** This is the output of: " +
                                              command + " ****** \n' > " + remote_file_path, host,  user,)
    ex.execute_unix_command_on_remote_as_root(command + " >> " + remote_file_path, host, user)
    transfer_file_from_remote(remote_file_path, remote_file_path, local_file_path, host, user)
    ex.execute_unix_command_on_remote_as_root("rm -f " + remote_file_path, host, user)


@Robot_log
def transfer_file_from_remote(remote_file_path, temp_file_path, local_file_path, host, user):
    """"
      This method is used to transfer a file  to the localhost, from a node other than the CRF_node_1.
      :param remote_file_path: full file path on the remote node
      :param temp_file_path: full file path on the CRF_node_1
      :param local_file_path: full file path on the localhost
      :param host: ip/hostname of the remote node
      :param user: this user is used with the scp command
    """
    scp_command = "scp " + user['username'] + "@" + host + ":" + remote_file_path + " " + temp_file_path
    sshlib.write(scp_command)
    sshlib.read_until(host + "'s password:")
    sshlib.write(user['password'])
    sshlib.read_until(user['prompt'])
    sshlib.get_file(temp_file_path, local_file_path)
    ex.execute_unix_command_as_root("rm -f " + temp_file_path)


def wait_for_healthy_kube_controller_manager():
        wait_until = datetime.now() + timedelta(seconds=180)
        command = "kubectl get componentstatus | grep controller-manager | grep Healthy | wc -l"
        result = ex.execute_unix_command_as_root(command)
        while (result < 1) and (datetime.now() < wait_until):
                logger.info("datetime.now:" + str(datetime.now()))
                logger.info("wait_until:" + str(wait_until))
                logger.info("Controller-manager is not healthy yet, waiting...")
                time.sleep(10)
                result = ex.execute_unix_command_as_root(command)
        if (result < 1):
                raise Exception("Controller-manager is not healthy!")


@Pabot_lock("health_check_1")
@Pabot_lock("modify_static_pod_config")
def modify_static_pod_config(operation,
                             manifest_file,
                             flags):
    """
    This method inserts/removes the given flag list into the manifest file of a static pod.

    :param manifest_file: manifest file name with extension present in /etc/kubernetes/manifests folder
    :param flags: flags which will be given to the executed command in the container
    :param operation: add or remove

    """
    crf_nodes = stack_infos.get_crf_nodes()
    if not crf_nodes:
        logger.info("Nodes dictionary is empty, nothing to check.")
        return
    logger.info("adding flag to pod file")
    for key in crf_nodes:
        ex.execute_unix_command_on_remote_as_root("\mv /etc/kubernetes/manifests/"
                                                  + manifest_file + " /tmp/" + manifest_file,
                                                  crf_nodes[key])
        file = ruamel.yaml.round_trip_load(ex.execute_unix_command_on_remote_as_root("cat /tmp/" + manifest_file,
                                                                                     crf_nodes[key]),
                                           preserve_quotes=True)
        for actual_flag in flags:
            operation(file, actual_flag)

        file = ruamel.yaml.round_trip_dump(file, default_flow_style=False)
    kube_controller_manager['obj_count'] = str(len(crf_nodes))
    check_kubernetes_object(kube_controller_manager, test_kubernetes_object_not_available, timeout=300)

    for key in crf_nodes:
        ex.execute_unix_command_on_remote_as_root("echo \"" + file + "\" > /etc/kubernetes/manifests/" + manifest_file,
                                                  crf_nodes[key])
        ex.execute_unix_command_on_remote_as_root("rm -f /tmp/" + manifest_file, crf_nodes[key])
    check_kubernetes_object(kube_controller_manager, test_kubernetes_object_available,
                            additional_filter="Running", timeout=300)
    wait_for_healthy_kube_controller_manager()


@Robot_log
def add_flag_to_command(yaml, flag):
    yaml["spec"]["containers"][0]["command"].append(flag)


@Robot_log
def remove_flag_from_command(yaml, flag):
    yaml["spec"]["containers"][0]["command"].remove(flag)


@Robot_log
def helm_install(chart_name, release_name, values=""):
    command = "helm install " + chart_name + " --name " + release_name
    if values:
        command += " --set " + values
    ex.execute_unix_command(command, fail_on_non_zero_rc=False)
    if helm_list(release_name) == '1':
        logger.info(chart_name + " chart is successfully installed")
    else:
        raise Exception(chart_name + " chart install has failed.")


@Robot_log
def helm_delete(release_name):
    ex.execute_unix_command("helm delete " + release_name + " --purge ", delay="30s", fail_on_non_zero_rc=False)
    if helm_list(release_name) == '0':
        logger.info(release_name + " chart is successfully deleted")
    else:
        raise Exception(release_name + " chart delete has failed.")


@Robot_log
def helm_list(release_name, add_check_arg=''):
    grep_arg = 'grep -w {}'.format(release_name)
    if add_check_arg != '':
        grep_arg += '| grep -w {}'.format(add_check_arg)
    command = "helm list --all | {} | wc -l".format(grep_arg)
    stdout, error_code = ex.execute_unix_command(command, fail_on_non_zero_rc=False)
    return stdout.strip()


@Robot_log
def check_kubernetes_object(kube_object, tester_function, additional_filter=".*", timeout=0, delay=0):
    """"
    This method executes kubectl get command with the given args, filters the output and checks the result with
      the given tester_function.
      :param kube_object: a dictionary, it represents a kubernetes objects,
                          obj_type, obj_name, namespace, obj_count keys are required.
      :param tester_function: this functoin checks the result and waits for the expected result
                              - kubernetes object exists or not - to happen in a given time
      :param additional_filter: use this regexp to filter further the results
      :param timeout: wait <timeout> seconds for the result
      :param delay: wait <delay> seconds before tester command
    """""
    command = "kubectl get {object} -n {ns_arg} 2>/dev/null | grep -w {name} | grep -E '{grep_arg}' | wc -l"
    command = command.format(object=kube_object['obj_type'], name=kube_object['obj_name'],
                             ns_arg=kube_object['namespace'], grep_arg=additional_filter)
    tester_function(kube_object, timeout, command, delay)


@Robot_log
def is_result_expected_within_given_time(command, expected_result, timeout, delay=0):
    time.sleep(delay)
    result = ex.execute_unix_command(command)
    if result == expected_result:
        return True
    wait_until = datetime.now() + timedelta(seconds=timeout)
    while result != expected_result and (datetime.now() < wait_until):
        logger.info("datetime.now:" + str(datetime.now()))
        logger.info("wait_until:" + str(wait_until))
        logger.info("expected result: " + expected_result)
        logger.info("result: " + result)
        time.sleep(1)
        result = ex.execute_unix_command(command)
        if result == expected_result:
            return True
    return False


def test_kubernetes_object_quality(kube_object, expected_result, filter=".*", timeout=30, delay=0):
    tester_command = "kubectl get " + kube_object['obj_type'] + " --all-namespaces | grep -w " + \
              kube_object['obj_name'] + " | grep -E '" + filter + "' | wc -l"
    res = is_result_expected_within_given_time(tester_command, expected_result, timeout, delay)
    if not res:
        log_command = "kubectl get " + kube_object['obj_type'] + " --all-namespaces | grep -w " + \
                         kube_object['obj_name']
        res = ex.execute_unix_command(log_command)
        ex.execute_unix_command("kubectl describe " + kube_object['obj_type'] + " " + kube_object['obj_name'] + " -n " +
                                kube_object['namespace'])
        raise Exception("Not " + kube_object['obj_count'] + " " + kube_object['obj_type'] + " " +
                        kube_object['obj_name'] + " is in expected (" + filter + ") state:" + res)
    logger.console(kube_object['obj_count'] + " " + kube_object['obj_type'] + " " + kube_object['obj_name'] +
                   " is in expected (" + filter + ") state.")


def test_kubernetes_object_available(kube_object, timeout, tester_command, delay=0):
    res = is_result_expected_within_given_time(tester_command, kube_object['obj_count'], timeout=timeout, delay=delay)
    if not res:
        describe_command = "kubectl describe " + kube_object['obj_type'] + " -n " + \
                           kube_object['namespace'] + " " + kube_object['obj_name']
        ex.execute_unix_command(describe_command, fail_on_non_zero_rc=False)
        raise Exception("Not " + kube_object['obj_count'] + " " + kube_object['obj_type'] + " " +
                        kube_object['obj_name'] + " is running!")
    logger.console(kube_object['obj_count'] + " " + kube_object['obj_type'] + " " + kube_object['obj_name'] +
                   " is running, as expected!")


def test_kubernetes_object_not_available(kube_object, timeout, tester_command, delay=0):
    res = is_result_expected_within_given_time(tester_command, expected_result="0", timeout=timeout, delay=delay)
    if not res:
        describe_command = "kubectl describe " + kube_object['obj_type'] + " -n " + \
                           kube_object['namespace'] + " " + kube_object['obj_name']
        ex.execute_unix_command(describe_command, fail_on_non_zero_rc=False)
        raise Exception("At least 1 " + kube_object['obj_type'] + " " + kube_object['obj_name'] + " still exists!")
    logger.console(kube_object['obj_type'] + " " + kube_object['obj_name'] + " does not exist, as expected!")


def is_node_under_pressure(nodeslog):
        if ((nodeslog.find("pressure")) != -1):
            return True
        else:
            return False


def wait_if_pressure(timeout=pressure_default_timeout):
        wait_until = datetime.now() + timedelta(seconds=timeout)
        command = "kubectl get nodes -o json | jq '.items[] | \"\(.metadata.name) \(.spec.taints)\"'"
        nodeslog = ex.execute_unix_command_as_root(command)
        while (is_node_under_pressure(nodeslog)) and (datetime.now() < wait_until):
            logger.info("datetime.now:" + str(datetime.now()))
            logger.info("wait_until:" + str(wait_until))
            logger.info("Node is under pressure found: " + nodeslog )
            time.sleep(10)
            nodeslog = ex.execute_unix_command_as_root(command)
        if is_node_under_pressure(nodeslog):
            raise Exception("Node pressure not resolved in time.")
        else:
            logger.info( nodeslog )


@Robot_log
def check_url_running(filename, url):
    command = "curl -s {url} > /dev/null ; echo -n $?"
    result = ex.execute_unix_command_as_root(command.format(url=url))
    if result == "0":
        logger.console("{url} is running!".format(url=url))
    else:
        gather_logs("curl -s {url}".format(url=url), filename, log_dir)
        raise Exception("{url} is not running !".format(url=url))


@Robot_log
def subprocess_cmd(command):
    return subprocess.check_output(command, shell=True).strip()


@Robot_log
def put_file(local_script_path, remote_script_path, permissions="777", user=root['username'], group=root['username']):
    ex.get_ssh_library_instance().put_file(local_script_path, remote_script_path, permissions)
    head, tail = os.path.split(remote_script_path)
    command = 'ls -l ' + head + ' | grep ' + tail + ' | wc -l'
    res = is_result_expected_within_given_time(command, expected_result="1", timeout=5)
    if not res:
        raise Exception("File not found at " + remote_script_path + "!")
    ex.execute_unix_command_as_root('chgrp ' + group + ' ' + remote_script_path)
    ex.execute_unix_command_as_root('chown ' + user + ' ' + remote_script_path)


@Robot_log
def get_helm_chart_content(chart_name):
    ex.execute_unix_command("helm fetch " + chart_name + " --untar --untardir /tmp")
    return ex.execute_unix_command("ls /tmp/" + chart_name.split('/')[1] +
                                   "/templates | awk -F . '{print $1}'").split('\r\n')


@Robot_log
def get_cpupools():
    node_map = {}
    node_list = ex.execute_unix_command("kubectl get nodes -L=nodename | awk '{print $6}'| tail -n +2")
    cmap_str = ex.execute_unix_command("kubectl get configmap -n kube-system {cm} -o yaml"
                                       .format(cm=cpu_pooling_cm_name))
    for nodename in node_list.splitlines():
        yamldict = yaml.load(cmap_str)
        for key in yamldict['data']:
            if nodename in yamldict['data'][key]:
                worker_yaml = yaml.load(yamldict['data'][key])
                pool_dict = {}
                if worker_yaml['pools']:
                    for pool in worker_yaml['pools']:
                        pool_str = worker_yaml['pools'][pool]['cpus']
                        pool_list = []
                        for sub_list in pool_str.split(','):
                            pool_list = pool_list + ([int(sub_list)] if '-' not in sub_list else
                                                     range(int(sub_list.split('-')[0]),
                                                           int(sub_list.split('-')[1]) + 1))
                        pool_dict[pool] = pool_list
                node_map[nodename] = pool_dict
    return node_map


@Robot_log
def get_cpu_allowed_list_from_pod(pod_name):
    bash_command = "cat /proc/1/status | grep Cpus_allowed_list"
    result = ex.execute_unix_command("kubectl exec `kubectl get pod | grep {0} | "
                                     "awk '{{print $1}}'` -- {1}".format(pod_name, bash_command))
    pool_list = []
    for cpu in result.split(':')[1].split(','):
        pool_list = pool_list + ([int(cpu)] if '-' not in cpu else range(int(cpu.split('-')[0]),
                                                                         int(cpu.split('-')[1]) + 1))
    return pool_list


@Robot_log
def allowed_cpus_is_in_cpu_pool(allowed_cpus, cpu_pool):
    for allowed in allowed_cpus:
        if allowed not in cpu_pool:
            return False
    return True


def decide_nodename():
    nodename = 'caas_worker1'
    command = "kubectl get node -L=nodename | awk {{'print $6'}} | tail -n +2"
    node_names = ex.execute_unix_command(command)
    if nodename not in node_names:
        return node_names.splitlines()[0]
    return nodename


@Robot_log
def determine_accurate_running_time_of_obj(object_type, object_name):
    hours = mins = secs = 0
    cmd = "kubectl get {obj_type} --all-namespaces --no-headers=true | grep {obj_name} | awk '{{print $NF}}'"\
        .format(obj_type=object_type, obj_name=object_name)
    resp = ex.execute_unix_command(cmd)
    time = re.findall(r'\d{0,2}h|\d{0,3}m|\d{1,3}s', resp)
    for t in time:
        if t[-1] == 'h':
            hours = int(t[:-1])
        elif t[-1] == 'm':
            mins = int(t[:-1])
        elif t[-1] == 's':
            secs = int(t[:-1])

    return datetime.now() - timedelta(hours=hours, minutes=mins, seconds=secs)
