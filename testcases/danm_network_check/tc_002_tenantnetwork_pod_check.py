import sys
import os
import common_utils
import danm_utils

from execute_command import execute_command
from decorators_for_robot_functionalities import *
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
infra_int_if = stack_infos.get_infra_int_if()
infra_ext_if = stack_infos.get_infra_ext_if()
infra_storage_if = stack_infos.get_infra_storage_if()


def tc_002_tenantnetwork_pod_check():
    steps = ['step1_check_static_ip_allocations',
             'step2_check_dynamic_ip_shortage',
             'step3_check_static_ip_shortage',
             'step4_check_attach_in_kubesystem_namespace',
             'step5_check_static_ip_alloc_static_routes_success_after_purge',
             'step6_check_step4_deletion_success',
             'step7_check_static_ip_alloc_outside_cidr',
             'step8_check_ip_alloc_with_cidrless_allocpoolless_tenantnet',
             'step9_check_connection_to_flannel_and_ipvlan_tenantnetworks',
             'step10_check_service_reachability_with_flannel',
             'step11_check_flannel_static_ip_alloc_not_in_flannel_cidr_ignored',
             'step12_none_ip_pod_restart_loop',
             'step13_check_invalid_net_attach_and_successful_damnep_ip_release_after_retries',
             'step14_check_realloc_ips_of_prev_step_with_dynamic_and_none_ip_alloc',
             'tc_002_tenantnetwork_pod_check.Teardown']

    BuiltIn().run_keyword("tc_002_tenantnetwork_pod_check.Setup")
    common_utils.keyword_runner(steps)


@pabot_lock("health_check_1")
def Setup():
    tennet_attach_test = common_utils.get_helm_chart_content("default/tenantnetwork-attach-test")
    danm_utils.compare_test_data(tennet_attach_test, tenantnetwork_attach_properties)

    replace_ifaces_in_fetched_chart_templates("/tmp/tenantnetwork-attach-test/templates/*")
    replace_ifaces_in_fetched_chart_templates("/tmp/tenantconfig-test/templates/*")
    # deploy a valid TenantConfig
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantconfig-test/templates/tconf_05.yaml")
    # remove the default TenantConfig
    execute.execute_unix_command("kubectl delete tenantconfig danm-tenant-config")
    # deploy all TenantNetwork-s
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-attach-test/templates")
    set_expected_host_if_in_constants(tenantnetwork_attach_properties)


@pabot_lock("health_check_1")
def Teardown():
    execute.execute_unix_command("kubectl create -f /var/lib/docker/manifests/infra/danm-tenant-config.yaml")
    execute.execute_unix_command("kubectl delete tenantconfig tconf-05")
    execute.execute_unix_command("kubectl delete -f /tmp/tenantnetwork-attach-test/templates/")


def step1_check_static_ip_allocations():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod1", release_name="tenantnetwork-attach-pod1")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod1,
                                                expected_result=tennet_pod1['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=60,
                                                delay=10)
    pod_list = danm_utils.get_pod_list(tennet_pod1)
    if set(tennet_pod1['ip_list']) != set(danm_utils.get_pod_ips(pod_list)):
        raise Exception("Static ip allocation for tenantnetwork-attach-pod1 was unsuccessful!")
    logger.info("Static ips allocated successfully!")
    danm_utils.check_mac_address(pod_list, 'tennet_attach_01', tenantnetwork_attach_properties)


def step2_check_dynamic_ip_shortage():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod2", release_name="tenantnetwork-attach-pod2")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod2,
                                                expected_result=tennet_pod2['obj_count'],
                                                filter=r'(ContainerCreating)\s*[0]',
                                                timeout=60)
    alloc_pool = danm_utils.get_alloc_pool('tennet_attach_01', tenantnetwork_attach_properties, 'tenantnetwork')
    danm_utils.check_dynamic_ips(alloc_pool, tennet_pod2['ip_list'])


def step3_check_static_ip_shortage():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod3", release_name="tenantnetwork-attach-pod3")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod3,
                                                expected_result=tennet_pod3['obj_count'],
                                                filter=r'(ContainerCreating)\s*[0]',
                                                timeout=30)
    common_utils.helm_delete("tenantnetwork-attach-pod2")
    common_utils.check_kubernetes_object(kube_object=tennet_pod2,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=60)
    common_utils.helm_delete("tenantnetwork-attach-pod1")


def step4_check_attach_in_kubesystem_namespace():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod4", release_name="tenantnetwork-attach-pod4")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod4,
                                                expected_result=tennet_pod4['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=60,
                                                delay=10)
    alloc_pool = danm_utils.get_alloc_pool("tennet_attach_02", tenantnetwork_attach_properties, 'tenantnetwork')
    danm_utils.check_dynamic_ips(alloc_pool, tennet_pod4['ip_list'])
    common_utils.helm_delete(release_name="tenantnetwork-attach-pod4")


def step5_check_static_ip_alloc_static_routes_success_after_purge():
    common_utils.check_kubernetes_object(kube_object=tennet_pod1,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=60)
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod3,
                                                expected_result=tennet_pod3['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=60)
    pod_list = danm_utils.get_pod_list(tennet_pod3)
    if set(tennet_pod3['ip_list']) != set(danm_utils.get_pod_ips(pod_list)):
        raise Exception("Static ip allocation for tenantnetwork-attach-pod3 was unsuccessful!")
    logger.info("Static ips allocated successfully!")

    danm_utils.check_static_routes(pod_list, 'tennet_attach_01', tenantnetwork_attach_properties)

    danm_utils.check_connectivity(pod_list, list(pod_list)[0], tennet_pod3['ip_list'])
    danm_utils.check_connectivity(pod_list, list(pod_list)[3], tennet_pod3['ip_list'])


@robot_log
def step6_check_step4_deletion_success():
    common_utils.check_kubernetes_object(kube_object=tennet_pod4,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=60)
    danm_utils.check_danmnet_endpoints_deleted(tennet_pod4, 'tennet_attach_02', tenantnetwork_attach_properties,
                                               tennet_pod4['ip_list'])


@robot_log
def step7_check_static_ip_alloc_outside_cidr():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod5", release_name="tenantnetwork-attach-pod5")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod5,
                                                expected_result=tennet_pod5['obj_count'],
                                                filter=r'(ContainerCreating)\s*[0]',
                                                timeout=90)


@robot_log
def step8_check_ip_alloc_with_cidrless_allocpoolless_tenantnet():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod6", release_name="tenantnetwork-attach-pod6")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod6,
                                                expected_result=tennet_pod6['obj_count'],
                                                filter=r'(ContainerCreating)\s*[0]',
                                                timeout=90)


@robot_log
def step9_check_connection_to_flannel_and_ipvlan_tenantnetworks():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod7", release_name="tenantnetwork-attach-pod7")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod7,
                                                expected_result=tennet_pod7['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=90)

    pod_list = danm_utils.get_pod_list(tennet_pod7)
    danm_utils.check_dynamic_ips(tenantnetwork_attach_properties['tennet_attach_04']['flannel_pool'],
                                 danm_utils.get_pod_ips(pod_list))

    alloc_pool = danm_utils.get_alloc_pool('tennet_attach_03', tenantnetwork_attach_properties, 'tenantnetwork')
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name=''))


@robot_log
def step10_check_service_reachability_with_flannel():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod8", release_name="tenantnetwork-attach-pod8")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod8,
                                                expected_result=tennet_pod8['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=90)
    command = "curl tennet-pod-08.default.svc.nokia.net:4242"
    res = execute.execute_unix_command_as_root(command)
    if "OK" not in res:
        raise Exception("NOK: tennet-pod-08 service is not reachable")
    logger.info("OK: tennet-pod-08 service is reachable")
    pod_list = danm_utils.get_pod_list(tennet_pod8)
    assigned_ips = danm_utils.get_pod_ips(pod_list)
    danm_utils.check_dynamic_ips(tenantnetwork_attach_properties['tennet_attach_04']['flannel_pool'], assigned_ips)


def step11_check_flannel_static_ip_alloc_not_in_flannel_cidr_ignored():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod9", release_name="tenantnetwork-attach-pod9")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod9,
                                                expected_result=tennet_pod9['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=90)


def step12_none_ip_pod_restart_loop():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod10",
                              release_name="tenantnetwork-attach-pod10")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod10,
                                                expected_result=tennet_pod10['obj_count'],
                                                filter=r'(ContainerCreating)\s*[0]',
                                                timeout=90)
    common_utils.helm_delete("tenantnetwork-attach-pod3")
    common_utils.helm_delete("tenantnetwork-attach-pod5")
    common_utils.helm_delete("tenantnetwork-attach-pod6")
    common_utils.helm_delete("tenantnetwork-attach-pod7")
    common_utils.helm_delete("tenantnetwork-attach-pod8")
    common_utils.helm_delete("tenantnetwork-attach-pod9")
    common_utils.helm_delete("tenantnetwork-attach-pod10")


def step13_check_invalid_net_attach_and_successful_damnep_ip_release_after_retries():
    tnet1_alloc_before = danm_utils.get_alloc_value('tennet_attach_01', tenantnetwork_attach_properties,
                                                    "tenantnetwork")
    tnet5_alloc_before = danm_utils.get_alloc_value('tennet_attach_05', tenantnetwork_attach_properties,
                                                    "tenantnetwork")
    tnet6_alloc_before = danm_utils.get_alloc_value('tennet_attach_06', tenantnetwork_attach_properties,
                                                    "tenantnetwork")
    common_utils.get_helm_chart_content("default/tenantnetwork-attach-pod11")
    common_utils.get_helm_chart_content("default/tenantnetwork-attach-pod13")

    for _ in range(0, 10):
        danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-attach-pod11/templates")
        danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-attach-pod13/templates")
        common_utils.test_kubernetes_object_quality(kube_object=tennet_pod11,
                                                    expected_result=tennet_pod11['obj_count'],
                                                    filter=r'(ContainerCreating)\s*[0]',
                                                    timeout=40)
        common_utils.test_kubernetes_object_quality(kube_object=tennet_pod13,
                                                    expected_result=tennet_pod13['obj_count'],
                                                    filter=r'(ContainerCreating)\s*[0]',
                                                    timeout=40)
        danm_utils.delete_resources_by_manifest_path("/tmp/tenantnetwork-attach-pod11/templates")
        danm_utils.delete_resources_by_manifest_path("/tmp/tenantnetwork-attach-pod13/templates")
        common_utils.check_kubernetes_object(kube_object=tennet_pod11,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=40)
        common_utils.check_kubernetes_object(kube_object=tennet_pod13,
                                             tester_function=common_utils.test_kubernetes_object_not_available,
                                             timeout=40)

    tnet1_alloc_after = danm_utils.get_alloc_value('tennet_attach_01', tenantnetwork_attach_properties, 'tenantnetwork')
    tnet5_alloc_after = danm_utils.get_alloc_value('tennet_attach_05', tenantnetwork_attach_properties, 'tenantnetwork')
    tnet6_alloc_after = danm_utils.get_alloc_value('tennet_attach_06', tenantnetwork_attach_properties, 'tenantnetwork')
    if tnet1_alloc_before != tnet1_alloc_after:
        raise Exception("allocation value in tennet_attach_01 is not as expected")
    if tnet5_alloc_before != tnet5_alloc_after:
        raise Exception("allocation value in tennet_attach_05 is not as expected")
    if tnet6_alloc_before != tnet6_alloc_after:
        raise Exception("allocation value in tennet_attach_06 is not as expected")
    danm_utils.check_dep_count('default', exp_count=0)


def step14_check_realloc_ips_of_prev_step_with_dynamic_and_none_ip_alloc():
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod12",
                              release_name="tenantnetwork-attach-pod12")
    common_utils.helm_install(chart_name="default/tenantnetwork-attach-pod14",
                              release_name="tenantnetwork-attach-pod14")
    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod12,
                                                expected_result=tennet_pod12['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=90)
    pod_list = danm_utils.get_pod_list(tennet_pod12)
    alloc_pool = danm_utils.get_alloc_pool("tennet_attach_01", tenantnetwork_attach_properties, "tenantnetwork")
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name='tnet_1'))
    alloc_pool = danm_utils.get_alloc_pool("tennet_attach_05", tenantnetwork_attach_properties, "tenantnetwork")
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name='eth0'))

    common_utils.test_kubernetes_object_quality(kube_object=tennet_pod14,
                                                expected_result=tennet_pod14['obj_count'],
                                                filter=r'(Running)\s*[0]',
                                                timeout=90)
    pod_list = danm_utils.get_pod_list(tennet_pod14)
    # danm_utils.check_dynamic_ips(alloc_pool, [tennet_pod14['ip_list'][2]])
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name='tnet5'))
    alloc_pool = danm_utils.get_alloc_pool("tennet_attach_06", tenantnetwork_attach_properties, "tenantnetwork")
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name='eth0'))
    alloc_pool = danm_utils.get_alloc_pool("tennet_attach_01", tenantnetwork_attach_properties, "tenantnetwork")
    danm_utils.check_dynamic_ips(alloc_pool, danm_utils.get_pod_ips(pod_list, if_name='tnet_2'))
    common_utils.helm_delete("tenantnetwork-attach-pod12")
    common_utils.helm_delete("tenantnetwork-attach-pod14")
    common_utils.check_kubernetes_object(kube_object=tennet_pod12,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=20)
    common_utils.check_kubernetes_object(kube_object=tennet_pod14,
                                         tester_function=common_utils.test_kubernetes_object_not_available,
                                         timeout=20)
    danm_utils.check_dep_count(tennet_pod12["namespace"], exp_count=0)


@robot_log
def replace_ifaces_in_fetched_chart_templates(path):
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_int_if }}/" + infra_int_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_ext_if }}/" + infra_ext_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_storage_if }}/" + infra_storage_if + "/g' " + path)


# TODO: figure out sg for host_if verif, make all v(x)lan and fill expected res in prop_dict
@robot_log
def set_expected_host_if_in_constants(properties_dict):
    for elem in properties_dict:
        properties_dict[elem]['host_if'] = infra_int_if
