import time
import json
import re
import os
import users

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from netaddr import IPAddress
from decorators_for_robot_functionalities import *


log_dir = os.path.join(os.path.dirname(__file__))
ex = BuiltIn().get_library_instance('execute_command')
sshlib = ex.get_ssh_library_instance()
stack_infos = BuiltIn().get_library_instance('stack_infos')
BuiltIn().import_library('pabot.PabotLib')
pabot = BuiltIn().get_library_instance('pabot.PabotLib')


@robot_log
def check_host_interfaces(network_properties_dict):
    for node, node_ip in stack_infos.get_all_nodes().items():
        logger.info("Checking host interfaces on " + node + ": " + node_ip)
        ex.ssh_to_another_node(node_ip, users.cloudadmin)
        for network in network_properties_dict:
            if (network_properties_dict[network]['host_if'] != ''):
                if (node == "compute-1" and network_properties_dict[network]['iface_type'] != 'int'):
                    continue
                command = "ip a | grep " + network_properties_dict[network]['host_if'] + " | wc -l"
                count = ex.execute_unix_command(command)
                if count != '1':
                    raise Exception("host interface check Failed, interface " +
                                    network_properties_dict[network]['host_if'] + " does not exist on " + node + ": " +
                                    node_ip)
                logger.info("host interface check OK, interface " + network_properties_dict[network]['host_if'] +
                            " exists on " + node)
            else:
                command = "ip a | grep " + network_properties_dict[network]['name'] + "[.:] | wc -l"
                count = ex.execute_unix_command(command)
                if count != '0':
                    raise Exception("host interface check Failed, " + network_properties_dict[network]['name'] +
                                    " related interface exists on node: " + node + ": " + node_ip)
                logger.info("host interface check OK, no unnecessary " + network_properties_dict[network]['name'] +
                            " related host interface exists on node: " + node + ": " + node_ip)
        ex.exit_from_user()


@robot_log
def create_resources_from_fetched_chart_templates(template_path):
    ex.execute_unix_command("kubectl create -f " + template_path, fail_on_non_zero_rc=False)


@robot_log
def delete_all_resources(resource_type):
    ex.execute_unix_command("kubectl delete " + resource_type + " --all")


@robot_log
def delete_resources_by_manifest_path(path):
    ex.execute_unix_command("kubectl delete -f " + path)


@robot_log
def get_resource_count(resource_type, resource_name):
    return ex.execute_unix_command("kubectl get " + resource_type + " 2>/dev/null | grep -w " + resource_name +
                                   " | wc -l")


@robot_log
def compare_test_data(list_to_compare, dict_to_compare):
    for danmnet in list_to_compare:
        if danmnet not in dict_to_compare:
            logger.warn(danmnet + " is not present in test constants: {}".format(dict_to_compare))
    for key in dict_to_compare:
        if key not in list_to_compare:
            logger.warn(key + " is not present in {} chart".format(list_to_compare))


@robot_log
def get_pod_list(kube_object):
    pod_list = {}
    command = "kubectl get pod --all-namespaces | grep -w " + kube_object[
        'obj_name'] + " | awk '{print $1 \" \" $2 \" \" $4 \" \" $5}'"
    for line in ex.execute_unix_command_as_root(command).split('\r\n'):
        pod_list[line.split(' ')[1]] = {'namespace': line.split(' ')[0], 'status': line.split(' ')[2],
                                        'restarts': line.split(' ')[3]}
    return pod_list


@robot_log
def get_pod_ips(pod_list, skip_restarts=False, if_name='eth0'):
    assigned_ips = []
    for key in pod_list:
        if (pod_list[key]['status'] == 'Running') and ((pod_list[key]['restarts'] == '0') or skip_restarts):
            logger.info(pod_list[key]['namespace'])
            if if_name != '':
                command = "kubectl exec " + key + " -n " + pod_list[key]['namespace'] + " ip a | grep " + if_name + \
                          " | grep inet | awk '{print $2}' | awk -F \"/\" '{print $1}' "
            else:
                command = "kubectl exec " + key + " -n " + pod_list[key]['namespace'] + "  -- ip -o a | " \
                          "grep -vE '(: lo|: eth0)' | grep inet | awk '{print $4}' | awk -F \"/\" '{print $1}'"
            assigned_ips.append(ex.execute_unix_command_as_root(command))
    return assigned_ips


@robot_log
def check_mac_address(pod_list, network, prop_dict):
    command = "ip a | grep -wA 1 " + prop_dict[network]['host_if'] + " | grep ether | awk '{print $2}'"
    host_mac = ex.execute_unix_command_as_root(command)
    for pod in pod_list:
        if (pod_list[pod]['status'] == 'Running') and (pod_list[pod]['restarts'] == '0'):
            command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " ip a | grep -A 1 eth0 | " \
                                                                                    "grep link | awk '{print $2}'"
            pod_mac = ex.execute_unix_command_as_root(command)
            if host_mac != pod_mac:
                raise Exception("Wrong Mac address in pod " + pod + "hostmac: " + host_mac + " ; podmac: " + pod_mac)
            logger.info("Correct mac address in pod " + pod)


@robot_log
def get_alloc_pool(network, dictionary, resource_type):
    alloc_pool = {}
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -n " + \
              dictionary[network]['namespace'] + " -o yaml " + \
              " | grep allocation_pool -A 2 | grep start | awk {'print$2'}"
    alloc_pool['start'] = ex.execute_unix_command_as_root(command)
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -n " + \
              dictionary[network]['namespace'] + " -o yaml " + \
              " | grep allocation_pool -A 2 | grep end | awk {'print$2'}"
    alloc_pool['end'] = ex.execute_unix_command_as_root(command)
    return alloc_pool


@robot_log
def check_dynamic_ips(alloc_pool, assigned_ips):
    for ip in assigned_ips:
        if (IPAddress(alloc_pool['start']) > IPAddress(ip)) or (IPAddress(ip) > IPAddress(alloc_pool['end'])):
            raise Exception("Dynamic ip: {} is not in allocation pool: {} - {}".format(ip, alloc_pool['start'],
                                                                                       alloc_pool['end']))
    logger.info("All dynamic ips are from the allocation pool.")
    if len((set(assigned_ips))) != len(assigned_ips):
        raise Exception("duplicated IPs assigned")
    logger.info("All allocated IPs are unique")


@robot_log
def check_static_routes(pod_list, network, properties_dict):
    for pod in pod_list:
        if (pod_list[pod]['status'] == 'Running') and (pod_list[pod]['restarts'] == '0'):
            command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " route | grep " + \
                      properties_dict[network]['routes'].split('/')[0] + " | grep " + \
                      properties_dict[network]['routes'].split(' ')[1] + " | wc -l"
            res = ex.execute_unix_command_as_root(command)
            if res != '1':
                raise Exception("static route in pod " + pod + " does not match with route defined in " + network)
            logger.info("Static route in pod " + pod + " is as it should be.")


@robot_log
def check_connectivity(pod_list, pod, ip_list):
    for ip in ip_list:
        command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " -- sh -c \"ping -c 1 " + ip + "\""
        stdout = ex.execute_unix_command_as_root(command)
        if '0% packet loss' not in stdout:
            raise Exception("pod " + pod + " cannot reach ip " + ip)
        logger.info("pod " + pod + " can reach ip " + ip)


@robot_log
def check_danmnet_endpoints_deleted(kube_object, network, properties_dict, assigned_ips):
    for ip in assigned_ips:
        command = "kubectl get danmep -n " + kube_object['namespace'] + " -o yaml | grep -B 10 " + \
                  properties_dict[network]['name'] + " | grep " + ip + " | wc -l"
        res = ex.execute_unix_command_as_root(command)
        if res != '0':
            raise Exception("Endpoint with ip " + ip + " still exists.")
    logger.info("The necessary endpoints are cleared")


@robot_log
def get_alloc_value(network, dictionary, resource_type):
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -o yaml | grep -w alloc | " \
                                                                                   "awk '{print $2}'"
    alloc = ex.execute_unix_command_as_root(command)
    return alloc


def check_danm_count(ip_count_before_parameter, cbr0_content1_parameter, tries):
    if tries == 5:
        raise Exception("Flannel ips are not cleared after pod deletion")
    else:
        tries = tries + 1
    command = "ls -lrt /var/lib/cni/networks/cbr0/ | wc -l"
    ip_count_after = ex.execute_unix_command_as_root(command)
    command = "ls -lrt /var/lib/cni/networks/cbr0/"
    cbr0_content2 = ex.execute_unix_command_as_root(command)
    ip_count_before = ip_count_before_parameter
    cbr0_content1 = cbr0_content1_parameter
    if ip_count_before != ip_count_after:
        logger.info(cbr0_content1)
        logger.info(cbr0_content2)
        time.sleep(30)
        check_danm_count(ip_count_before, cbr0_content1, tries)


@robot_log
def check_dep_count(namespace, exp_count, test_pod_name_pattern=r'^danmnet-pods'):
    tries = 0
    deps = get_deps(namespace)
    # test_pod_name_pattern = r'^danmnet-pods'
    danmnet_test_deps = [dep for dep in deps if is_dep_belongs_to_pod(dep, test_pod_name_pattern)]
    while (tries < 5) and (len(danmnet_test_deps) != exp_count):
        time.sleep(20)
        tries += 1
        deps = get_deps(namespace)
        danmnet_test_deps = [dep for dep in deps if is_dep_belongs_to_pod(dep, test_pod_name_pattern)]

    if len(danmnet_test_deps) != exp_count:
        raise Exception("Danm endpoint count is not as expected! Got: " + str(len(danmnet_test_deps)) + ", expected: " +
                        str(exp_count))
    logger.info("Danm endpoint count is as expected.")


@robot_log
def get_deps(namespace):
    command = "kubectl get dep -n {} -o json".format(namespace)
    deps_text = ex.execute_unix_command_as_root(command)
    return json.loads(deps_text).get("items")


@robot_log
def is_dep_belongs_to_pod(dep, pod_pattern):
    pod_name = dep["spec"]["Pod"]
    return bool(re.search(pod_pattern, pod_name))
