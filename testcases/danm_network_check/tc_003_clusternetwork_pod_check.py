import sys
import os
import time
import json
import re
import common_utils
import danm_utils

from robot.libraries.BuiltIn import BuiltIn
from netaddr import IPAddress
from robot.api import logger
from execute_command import execute_command
from decorators_for_robot_functionalities import *
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
flannel_pool = {'start': '10.244.0.1', 'end': '10.244.255.254'}
static_ips = ["10.5.1.11", "10.5.1.19", "10.5.1.20", "10.5.255.254", ]
infra_int_if = stack_infos.get_infra_int_if()
infra_ext_if = stack_infos.get_infra_ext_if()
infra_storage_if = stack_infos.get_infra_storage_if()


def tc_003_clusternetwork_pod_check():
    """
        danmnet_pods1: pods attached to d_test-net2 with static ips
        danmnet_pods2: pods attached to d_test-net2 with dynamic ips
        danmnet_pods3: pods attached to d_test-net2 with the same static ips as danmnet-pods1
        danmnet_pods4: pods attached to ks_test-net2 with dynamic ips (kube-system namespace)
        danmnet_pods5: pod attached to d_test-net2 with static ip, ip is not in CIDR
        danmnet_pods6: pods attached to d_test-net1 with dynamic ips (no CIDR/alloc pool is defined in test-net1 )
        danmnet_pods7: pods attached to d_test-net24(flannel) and d_test-net7(ipvlan) networks with dynamic ip
        danmnet_pods8: pods attached to d_test-net24(flannel) with dynamic ip and service defined
        danmnet_pods9: pods attached to d_test-net24(flannel) with static ip(ignored)
        danmnet_pods10: pods attached to d_test-net2 with none ip
        danmnet_pods11: pod attached to d_test-net30 with static ip, d_test-net8 with none ip, none existing
        danmnet(error)
        danmnet_pods12: pod attached to d_test-net30 with static ip, d_test-net8 with dynamic ip, d_test-net25 with
        none ip
        danmnet_pods13: pod attached to d_test-net8 with static ip, d_test-net24(flannel) with dynamic ip, none existing
        danmnet(error)
        danmnet_pods14: pod attached to d_test-net25 with static ip, d_test-net24(flannel) with dynamic ip

        danmnet_pods1: pods attached to cnet-pod1 with static ips
        danmnet_pods2: pods attached to cnet-pod1 with dynamic ips
        danmnet_pods3: pods attached to cnet-pod1 with the same static ips as danmnet-pods1
        danmnet_pods4: pods attached to ks_test-net2 with dynamic ips (kube-system namespace)
        danmnet_pods5: pod attached to cnet-pod1 with static ip, ip is not in CIDR
        danmnet_pods6: pods attached to d_test-net1 with dynamic ips (no CIDR/alloc pool is defined in test-net1 )
        danmnet_pods7: pods attached to d_test-net24(flannel) and d_test-net7(ipvlan) networks with dynamic ip
        danmnet_pods8: pods attached to d_test-net24(flannel) with dynamic ip and service defined
        danmnet_pods9: pods attached to d_test-net24(flannel) with static ip(ignored)
        danmnet_pods10: pods attached to cnet-pod1 with none ip
        danmnet_pods11: pod attached to d_test-net30 with static ip, d_test-net8 with none ip,
        none existing danmnet(error)
        danmnet_pods12: pod attached to d_test-net30 with static ip, d_test-net8 with dynamic ip,
        d_test-net25 with none ip
        danmnet_pods13: pod attached to d_test-net8 with static ip, d_test-net24(flannel) with dynamic ip,
        none existing danmnet(error)
        danmnet_pods14: pod attached to d_test-net25 with static ip, d_test-net24(flannel) with dynamic ip


    """
    steps = ['step1', 'step2', 'step3', 'step5', 'step7', 'step8', 'step9', 'step10', 'step11', 'step12', 'step13',
             'step14', 'tc_003_clusternetwork_pod_check.Teardown']

    BuiltIn().run_keyword("tc_003_clusternetwork_pod_check.Setup")
    common_utils.keyword_runner(steps)


def Setup():
    # execute.execute_unix_command("kubectl create -f /tmp/clusternetwork-test/templates/cnet_attach.yaml")
    network_attach_test = common_utils.get_helm_chart_content("default/network-attach-test")
    compare_test_data(network_attach_test, network_attach_properties)
    replace_ifaces_in_fetched_chart_templates("/tmp/network-attach-test/templates/*")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/network-attach-test/templates")

    install_chart(danmnet_pods1)
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods1,
                                                expected_result=danmnet_pods1['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)
    install_chart(danmnet_pods2)
    install_chart(danmnet_pods3)
    # install_chart(danmnet_pods4)
    install_chart(danmnet_pods5)
    install_chart(danmnet_pods6)
    install_chart(danmnet_pods7)
    install_chart(danmnet_pods8)
    install_chart(danmnet_pods9)
    install_chart(danmnet_pods10)


def Teardown():
    common_utils.helm_delete("danmnet-pods12")
    common_utils.helm_delete("danmnet-pods14")
    danm_utils.delete_resources_by_manifest_path("/tmp/network-attach-test/templates/")


def step1():
    # Install danmnet_pods1: all of the pods should be in Running state, check static ips, mac address
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods1,
                                                expected_result=danmnet_pods1['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90,
                                                delay=10)
    pod_list = get_pod_list(danmnet_pods1)
    danmnet_pods1['ip_list'] = get_pod_ips(pod_list)
    if set(danmnet_pods1['ip_list']) != set(static_ips):
        raise Exception("Static ip allocation for danmnet-pods1 was not successful, assigned ips!")
    logger.info("Static ip allocation for danmnet-pods1 was successful")
    check_mac_address(pod_list, 'cnet_pod1')


def step2():
    # Install danmnet_pods2: ips already used from allocation pool -> 3 pods in containercreating state, check remaining
    # assigned ips in allocation pool
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods2,
                                                expected_result=danmnet_pods2['obj_count'],
                                                filter='(ContainerCreating)\s*[0]',
                                                timeout=90)
    pod_list = get_pod_list(danmnet_pods2)
    alloc_pool = get_alloc_pool('cnet_pod1', network_attach_properties, 'clusternetwork')
    danmnet_pods2['ip_list'] = get_pod_ips(pod_list)
    check_dynamic_ips(alloc_pool, danmnet_pods2['ip_list'])


def step3():
    # Danmnet_pods3 pods are not running because static ips are already allocated
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods3,
                                                expected_result=danmnet_pods3['obj_count'],
                                                filter='(ContainerCreating)\s*[0]',
                                                timeout=90)
    # Delete danmnet_pods1, danmnet_pods2
    common_utils.helm_delete("danmnet-pods2")
    common_utils.check_kubernetes_object(kube_object=danmnet_pods2,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=90)
    common_utils.helm_delete("danmnet-pods1")


def step5():
    # Check danmnet_pods1, danmnet_pods2 are purged, ips are reallocated for danmnet_pods3

    common_utils.check_kubernetes_object(kube_object=danmnet_pods1,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=90)
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods3,
                                                expected_result=danmnet_pods3['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=60)
    pod_list = get_pod_list(danmnet_pods3)
    assigned_ips = get_pod_ips(pod_list, skip_restarts=True)
    if set(assigned_ips) != set(static_ips):
        raise Exception("Static ip allocation for danmnet-pods3 was not successful!")
    logger.info("Static ip allocation for danmnet-pods3 was successful")
    check_static_routes(pod_list, 'cnet_pod1')

    actual_pod = list(pod_list)[0]
    check_connectivity(pod_list, actual_pod, static_ips)
    actual_pod = list(pod_list)[3]
    check_connectivity(pod_list, actual_pod, static_ips)


def step6():
    common_utils.check_kubernetes_object(kube_object=danmnet_pods4,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=90)
    check_danmnet_endpoints(danmnet_pods4, 'test-net2', danmnet_pods4['ip_list'])


def step7():
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods5,
                                                expected_result=danmnet_pods5['obj_count'],
                                                filter='(ContainerCreating)\s*[0]',
                                                timeout=90)


def step8():
    # Dynamic ip allocation fails if no CIDR/allocation pool defined
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods6,
                                                expected_result=danmnet_pods6['obj_count'],
                                                filter='(ContainerCreating)\s*[0]',
                                                timeout=90)


def step9():
    # multiple interfaces, check flannel and ipvlan ip allocation
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods7,
                                                expected_result=danmnet_pods7['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)
    pod_list = get_pod_list(danmnet_pods7)
    assigned_ips = get_pod_ips(pod_list)
    check_dynamic_ips(flannel_pool, assigned_ips)

    alloc_pool = get_alloc_pool('cnet_pod3', network_attach_properties, 'clusternetwork')
    assigned_ips = get_pod_ips(pod_list, if_name='')
    check_dynamic_ips(alloc_pool, assigned_ips)


def step10():
    # Check service is reachable with flannel
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods8,
                                                expected_result=danmnet_pods8['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)
    command = "curl danmnet-pods8-1.default.svc.nokia.net:4242"
    res = execute.execute_unix_command_as_root(command)
    if "OK" not in res:
        raise Exception("NOK: danmnet-pods8-1 service is not reachable")
    logger.info("OK: danmnet-pods8-1 service is reachable")
    pod_list = get_pod_list(danmnet_pods8)
    assigned_ips = get_pod_ips(pod_list)
    check_dynamic_ips(flannel_pool, assigned_ips)


def step11():
    # Static ip allocation is ignored with flannel
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods9,
                                                expected_result=danmnet_pods9['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)


def step12():
    # None ip, pod is restarting
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods10,
                                                expected_result=danmnet_pods10['obj_count'],
                                                filter='(ContainerCreating)\s*[0]',
                                                timeout=90)
    common_utils.helm_delete("danmnet-pods3")
    common_utils.helm_delete("danmnet-pods4")
    common_utils.helm_delete("danmnet-pods5")
    common_utils.helm_delete("danmnet-pods6")
    common_utils.helm_delete("danmnet-pods7")
    common_utils.helm_delete("danmnet-pods8")
    common_utils.helm_delete("danmnet-pods9")
    common_utils.helm_delete("danmnet-pods10")
    common_utils.check_kubernetes_object(kube_object=danmnet_pods_all,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=20)
    check_dep_count(danmnet_pods1["namespace"], exp_count=0)


@Pabot_lock("pv_test_ip")
@Pabot_lock("flannel_ip")
@Pabot_lock("flannel_ip2")
def step13():
    # danmnet_pods11, danmnet_pods13 has invalid networks attached hance the pod creation will fail,
    # checking if danmnet endpoints, ips are cleared after several unsuccessful pod creations
    alloc_before_cnet_pod5 = get_alloc_value('cnet_pod5', network_attach_properties, 'clusternetwork')
    alloc_before_cnet_pod6 = get_alloc_value('cnet_pod6', network_attach_properties, 'clusternetwork')
    common_utils.get_helm_chart_content('default/' + danmnet_pods11['obj_name'])
    common_utils.get_helm_chart_content('default/' + danmnet_pods13['obj_name'])
    command = "ls -rt /var/lib/cni/networks/cbr0/ | wc -l"
    ip_count_before = execute.execute_unix_command_as_root(command)
    command = "ls -rt /var/lib/cni/networks/cbr0/"
    cbr0_content1 = execute.execute_unix_command_as_root(command)

    for i in range(0, 10):
        # danmnet_pods11 creation fails
        command = "kubectl create -f /tmp/" + danmnet_pods11['obj_name'] + "/templates"
        execute.execute_unix_command_as_root(command)

        # danmnet_pods13 creation fails
        command = "kubectl create -f /tmp/" + danmnet_pods13['obj_name'] + "/templates"
        execute.execute_unix_command_as_root(command)
        common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods11,
                                                    expected_result=danmnet_pods11['obj_count'],
                                                    filter='(ContainerCreating)\s*[0]',
                                                    timeout=40)
        common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods13,
                                                    expected_result=danmnet_pods13['obj_count'],
                                                    filter='(ContainerCreating)\s*[0]',
                                                    timeout=40)
        command = "kubectl delete -f /tmp/" + danmnet_pods11['obj_name'] + "/templates"
        execute.execute_unix_command_as_root(command)
        command = "kubectl delete -f /tmp/" + danmnet_pods13['obj_name'] + "/templates"
        execute.execute_unix_command_as_root(command)
        common_utils.check_kubernetes_object(kube_object=danmnet_pods11,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=40)
        common_utils.check_kubernetes_object(kube_object=danmnet_pods13,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=40)
    check_danm_count(ip_count_before, cbr0_content1, 0)
    logger.info("All flannel ips are cleared")
    alloc_after_cnet_pod5 = get_alloc_value('cnet_pod5', network_attach_properties, 'clusternetwork')
    alloc_after_cnet_pod6 = get_alloc_value('cnet_pod6', network_attach_properties, 'clusternetwork')
    if alloc_after_cnet_pod6 != alloc_before_cnet_pod6:
        raise Exception("allocation value in cnet-pod6 is not as expected")
    if alloc_after_cnet_pod5 != alloc_before_cnet_pod5:
        raise Exception("allocation value in cnet-pod5 is not as expected")
    check_dep_count('default', exp_count=0)


def step14():
    # Static ip, dynamic ip allocation and none ip in the same pod
    # Check if the same ips can be allocated, which were failing in step 13
    install_chart(danmnet_pods12)
    install_chart(danmnet_pods14)
    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods12,
                                                expected_result=danmnet_pods12['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)
    pod_list = get_pod_list(danmnet_pods12)
    alloc_pool = get_alloc_pool('cnet_pod6', network_attach_properties, 'clusternetwork')
    danmnet_pods12['ip_list'] = get_pod_ips(pod_list, if_name='eth1')
    check_dynamic_ips(alloc_pool, danmnet_pods12['ip_list'])
    danmnet_pods12['ip_list'] = get_pod_ips(pod_list, if_name='eth0')
    if IPAddress(danmnet_pods12['ip_list'][0]) != IPAddress('10.10.0.250'):
        raise Exception("static ip in pod danmnet-pods12 is not as expected")

    common_utils.test_kubernetes_object_quality(kube_object=danmnet_pods14,
                                                expected_result=danmnet_pods14['obj_count'],
                                                filter='(Running)\s*[0]',
                                                timeout=90)
    pod_list = get_pod_list(danmnet_pods14)
    danmnet_pods14['ip_list'] = get_pod_ips(pod_list, if_name='eth2')
    if IPAddress(danmnet_pods14['ip_list'][0]) != IPAddress('10.10.0.254'):
        raise Exception("static ip in pod danmnet-pods14 is not as expected")
    common_utils.helm_delete("danmnet-pods12")
    common_utils.helm_delete("danmnet-pods14")
    common_utils.check_kubernetes_object(kube_object=danmnet_pods14,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=20)
    check_dep_count(danmnet_pods12["namespace"], exp_count=0)


@Robot_log
def check_danm_count(ip_count_before_parameter, cbr0_content1_parameter, tries):
    command = "ls -rt /var/lib/cni/networks/cbr0/"
    cbr0_content2 = execute.execute_unix_command_as_root(command)
    if tries == 3:
        diff = list(set(cbr0_content1_parameter) - set(cbr0_content2))
        logger.info("Additional IPs after step: " + diff)
        for ip in diff:
            command = "cat /var/lib/cni/networks/cbr0/" + ip + " | grep -v eth"
            cid = execute.execute_unix_command(command)
            command = "docker ps -a --no-trunc | grep " + cid
            docker_ps = execute.execute_unix_command(command)
            logger.info("Additional ip belongs to the following container: " + docker_ps)
        raise Exception("Flannel ips are not cleared after pod deletion")
    else:
        tries = tries + 1
    command = "ls -rt /var/lib/cni/networks/cbr0/ | wc -l"
    ip_count_after = execute.execute_unix_command_as_root(command)
    ip_count_before = ip_count_before_parameter
    cbr0_content1 = cbr0_content1_parameter
    if ip_count_before != ip_count_after:
        logger.info(cbr0_content1)
        logger.info(cbr0_content2)
        time.sleep(30)
        check_danm_count(ip_count_before, cbr0_content1, tries)


def install_chart(kube_object):
    common_utils.helm_install(chart_name="default/" + kube_object['obj_name'], release_name=kube_object['obj_name'])


@Robot_log
def get_pod_ips(pod_list, skip_restarts=False, if_name='eth0'):
    assigned_ips = []
    for key in pod_list:
        if (pod_list[key]['status'] == 'Running') and ((pod_list[key]['restarts'] == '0') or skip_restarts):
            logger.info(pod_list[key]['namespace'])
            if if_name != '':
                command = "kubectl exec " + key + " -n " + pod_list[key]['namespace'] + " ip a | grep " + if_name + \
                          " | grep inet | awk '{print $2}' | awk -F \"/\" '{print $1}' "
            else:
                command = "kubectl exec " + key + " -n " + pod_list[key]['namespace'] + \
                          "  -- ip -o a | grep -vE '(: lo|: eth0)' | grep inet | awk '{print $4}' | " \
                          "awk -F \"/\" '{print $1}'"
            assigned_ips.append(execute.execute_unix_command_as_root(command))
    return assigned_ips


@Robot_log
def get_alloc_pool(network, dictionary, resource_type):
    alloc_pool = {}
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -o yaml " + \
              " | grep allocation_pool -A 2 | grep start | awk {'print$2'}"
    alloc_pool['start'] = execute.execute_unix_command_as_root(command)
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -o yaml " + \
              " | grep allocation_pool -A 2 | grep end | awk {'print$2'}"
    alloc_pool['end'] = execute.execute_unix_command_as_root(command)
    return alloc_pool


@Robot_log
def get_pod_list(kube_object):
    pod_list = {}
    command = "kubectl get pod --all-namespaces | grep -w " + kube_object[
        'obj_name'] + " | awk '{print $1 \" \" $2 \" \" $4 \" \" $5}'"
    for line in execute.execute_unix_command_as_root(command).split('\r\n'):
        pod_list[line.split(' ')[1]] = {'namespace': line.split(' ')[0], 'status': line.split(' ')[2],
                                        'restarts': line.split(' ')[3]}
    return pod_list


@Robot_log
def check_dynamic_ips(alloc_pool, assigned_ips):
    for ip in assigned_ips:
        if (IPAddress(alloc_pool['start']) > IPAddress(ip)) or (IPAddress(ip) > IPAddress(alloc_pool['end'])):
            raise Exception("Dynamic ip is not in allocation pool")
    logger.info("All dynamic ips are from the allocation pool.")
    if len(list(set(assigned_ips))) != len(assigned_ips):
        raise Exception("duplicated IPs assigned")
    logger.info("All allocated IPs are unique")


@Robot_log
def check_static_routes(pod_list, danmnet):
    for pod in pod_list:
        if (pod_list[pod]['status'] == 'Running') and (pod_list[pod]['restarts'] == '0'):
            command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " route | grep " + \
                      network_attach_properties[danmnet]['routes'].split('/')[0] + " | grep " + \
                      network_attach_properties[danmnet]['routes'].split(' ')[1] + " | wc -l"
            res = execute.execute_unix_command_as_root(command)
            if res != '1':
                raise Exception("static route in pod " + pod + " does not match with route defined in " + danmnet)
            logger.info("Static route in pod " + pod + " is as it should be.")


@Robot_log
def check_mac_address(pod_list, network):
    command = "ip a | grep -wA 1 " + network_attach_properties[network]['host_if'] + " | grep ether | awk '{print $2}'"
    host_mac = execute.execute_unix_command_as_root(command)
    for pod in pod_list:
        if (pod_list[pod]['status'] == 'Running') and (pod_list[pod]['restarts'] == '0'):
            command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " ip a | grep -A 1 eth0 | " \
                                                                                    "grep link | awk '{print $2}'"
            pod_mac = execute.execute_unix_command_as_root(command)
            if host_mac != pod_mac:
                raise Exception("Wrong Mac address in pod " + pod)
            logger.info("Correct mac address in pod " + pod)


@Robot_log
def check_danmnet_endpoints(kube_object, network, assigned_ips):
    for ip in assigned_ips:
        command = "kubectl get danmep -n " + kube_object['namespace'] + " -o yaml | grep -B 10 " + \
                  network_attach_properties[network]['name'] + " | grep " + ip + " | wc -l"
        res = execute.execute_unix_command_as_root(command)
        if res != '0':
            raise Exception("Endpoint with ip " + ip + " still exists.")
    logger.info("The necessary endpoints are cleared")


@Robot_log
def check_connectivity(pod_list, pod, ip_list):
    for ip in ip_list:
        command = "kubectl exec " + pod + " -n " + pod_list[pod]['namespace'] + " -- sh -c \"ping -c 1 " + ip + "\""
        stdout = execute.execute_unix_command_as_root(command)
        if '0% packet loss' not in stdout:
            raise Exception("pod " + pod + " cannot reach ip " + ip)
        logger.info("pod " + pod + " can reach ip " + ip)


@Robot_log
def check_dep_count(namespace, exp_count):
    tries = 0
    danm_eps = get_deps(namespace)
    test_pod_name_pattern = r'^danmnet-pods'
    danmnet_test_deps = [dep for dep in danm_eps if is_dep_belongs_to_pod(dep, test_pod_name_pattern)]
    while (tries < 5) and (len(danmnet_test_deps) != exp_count):
        time.sleep(20)
        tries += 1
        danm_eps = get_deps(namespace)
        danmnet_test_deps = [dep for dep in danm_eps if is_dep_belongs_to_pod(dep, test_pod_name_pattern)]

    if len(danmnet_test_deps) != exp_count:
        raise Exception("Danm endpoint count is not as expected! Got: " + str(len(danmnet_test_deps)) + ", expected: " +
                        str(exp_count))
    logger.info("Danm endpoint count is as expected.")


@Robot_log
def get_deps(namespace):
    command = "kubectl get dep -n {} -o json".format(namespace)
    deps_text = execute.execute_unix_command_as_root(command)
    return json.loads(deps_text).get("items")


@Robot_log
def is_dep_belongs_to_pod(dep, pod_pattern):
    pod_name = dep["spec"]["Pod"]
    return bool(re.search(pod_pattern, pod_name))


@Robot_log
def get_alloc_value(network, dictionary, resource_type):
    command = "kubectl get " + resource_type + " " + dictionary[network]['name'] + " -o yaml | grep -w alloc | " \
                                                                                   "awk '{print $2}'"
    alloc = execute.execute_unix_command_as_root(command)
    return alloc


@Robot_log
def replace_ifaces_in_fetched_chart_templates(path):
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_int_if }}/" + infra_int_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_ext_if }}/" + infra_ext_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_storage_if }}/" + infra_storage_if + "/g' " + path)


@Robot_log
def compare_test_data(list_to_compare, dict_to_compare):
    for danmnet in list_to_compare:
        if danmnet not in dict_to_compare:
            logger.warn(danmnet + " is not present in test constants: {}".format(dict_to_compare))
    for key in dict_to_compare:
        if key not in list_to_compare:
            logger.warn(key + " is not present in {} chart".format(list_to_compare))


@Robot_log
def delete_all_resources(resource_type):
    execute.execute_unix_command("kubectl delete " + resource_type + " --all")
