import sys
import os
import common_utils
import danm_utils

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from execute_command import execute_command
from decorators_for_robot_functionalities import *
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

execute = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
infra_int_if = stack_infos.get_infra_int_if()
infra_ext_if = stack_infos.get_infra_ext_if()
infra_storage_if = stack_infos.get_infra_storage_if()


def tc_001_danmnet_object_check():
    steps = ['step1_inspect_clusternetworks',
             'step2_inspect_tenantconfigs',
             'step3_inspect_tenantnetworks'
             ]
    BuiltIn().run_keyword("tc_001_danmnet_object_check.Setup")
    common_utils.keyword_runner(steps)


def Setup():
    cnet_test = common_utils.get_helm_chart_content("default/clusternetwork-test")
    danm_utils.compare_test_data(cnet_test, clusternetworks_properties)

    cnet_test_error = common_utils.get_helm_chart_content("default/clusternetwork-test-error")
    danm_utils.compare_test_data(cnet_test_error, clusternetworks_error_properties)

    tenantconfig_test = common_utils.get_helm_chart_content("default/tenantconfig-test")
    danm_utils.compare_test_data(tenantconfig_test, tenantconfig_properties)

    tenantconfig_test_error = common_utils.get_helm_chart_content("default/tenantconfig-test-error")
    danm_utils.compare_test_data(tenantconfig_test_error, tenantconfig_error_properties)

    tenantnetwork_test = common_utils.get_helm_chart_content("default/tenantnetwork-test")
    danm_utils.compare_test_data(tenantnetwork_test, tenantnetwork_properties)

    tenantnetwork_test_error = common_utils.get_helm_chart_content("default/tenantnetwork-test-error")
    danm_utils.compare_test_data(tenantnetwork_test_error, tenantnetwork_error_properties)


def step1_inspect_clusternetworks():
    logger.info("Deploying valid ClusterNetwork manifests fetched from helm chart \'clusternetwork-test\'.")
    replace_ifaces_in_fetched_chart_templates("/tmp/clusternetwork-test/templates/*")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/clusternetwork-test/templates")
    for cnet in clusternetworks_properties:
        cnet_name = clusternetworks_properties[cnet]['name']
        count = danm_utils.get_resource_count(resource_type="clusternetwork", resource_name=cnet_name)
        if count == '0':
            raise Exception("ClusterNetwork " + cnet_name + " does not exist, but it should!")
        logger.info("ClusterNetwork " + cnet_name + " exists as expected.")
    danm_utils.check_host_interfaces(clusternetworks_properties)

    logger.info("Deploying invalid ClusterNetwork manifests fetched from helm chart \'clusternetwork-test-error\'."
                " All should fail.")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/clusternetwork-test-error/templates")
    for cnet in clusternetworks_error_properties:
        cnet_name = clusternetworks_error_properties[cnet]['name']
        count = danm_utils.get_resource_count(resource_type="clusternetworks", resource_name=cnet_name)
        if count != '0':
            raise Exception("ClusterNetwork " + cnet_name + " exists, but it should not!")
        logger.info("ClusterNetwork " + cnet_name + " does not exist, as expected.")

    danm_utils.delete_resources_by_manifest_path("/tmp/clusternetwork-test/templates")


def step2_inspect_tenantconfigs():
    logger.info("Deploying valid TenantConfig manifests fetched from helm chart \'tenantconfig-test\'.")
    replace_ifaces_in_fetched_chart_templates("/tmp/tenantconfig-test/templates/*")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantconfig-test/templates")
    for tconf in tenantconfig_properties:
        tconf_name = tenantconfig_properties[tconf]['name']
        count = danm_utils.get_resource_count(resource_type="tenantconfig", resource_name=tconf_name)
        if count == '0':
            raise Exception("TenantConfig " + tconf_name + " does not exist, but it should!")
        logger.info("TenantConfig " + tconf_name + " exists as expected.")

    logger.info("Deploying invalid TenantConfig manifests fetched from helm chart \'tenantconfig-test-error\'. "
                "All should fail.")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantconfig-test-error/templates")
    for tconf in tenantconfig_error_properties:
        tconf_name = tenantconfig_error_properties[tconf]['name']
        count = danm_utils.get_resource_count(resource_type="tenantconfig", resource_name=tconf_name)
        if count != '0':
            raise Exception("TenantConfig " + tconf_name + " exists, but it shouldn't!")
        logger.info("TenantConfig " + tconf_name + " does not exist, as expected.")


@pabot_lock("health_check_1")
def step3_inspect_tenantnetworks():
    danm_utils.delete_all_resources("tenantconfig")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantconfig-test/templates/tconf_05.yaml")

    # TenantNetwork-s with TenantConfig without vlan/vxlan
    logger.info("Deploying valid TenantNetwork manifests fetched from helm chart \'tenantnetwork-test\'.")
    replace_ifaces_in_fetched_chart_templates("/tmp/tenantnetwork-test/templates/*")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-test/templates")
    for tnet in tenantnetwork_properties:
        tnet_name = tenantnetwork_properties[tnet]['name']
        count = danm_utils.get_resource_count(resource_type="tenantnetwork", resource_name=tnet_name)
        if count == '0':
            raise Exception("TenantNetwork " + tnet_name + " does not exist, but it should!")
        logger.info("TenantNetwork " + tnet_name + " exists as expected.")

    logger.info("Deploying invalid TenantNetwork manifests fetched from helm chart \'tenantnetwork-test-error\'. "
                "All should fail.")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-test-error/templates")
    for tnet in tenantnetwork_error_properties:
        tnet_name = tenantnetwork_error_properties[tnet]['name']
        count = danm_utils.get_resource_count(resource_type="tenantnetwork", resource_name=tnet_name)
        if count != '0':
            raise Exception("TenantNetwork " + tnet_name + " exists, but it shouldn't!")
        logger.info("TenantNetwork " + tnet_name + " does not exist, as expected.")

    danm_utils.delete_resources_by_manifest_path("/tmp/tenantnetwork-test/templates")
    # TenantNetwork-s with TenantConfig with vlan/vxlan
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantconfig-test/templates/tconf_07.yaml")
    danm_utils.delete_resources_by_manifest_path("/tmp/tenantconfig-test/templates/tconf_05.yaml")
    danm_utils.create_resources_from_fetched_chart_templates("/tmp/tenantnetwork-test/templates/")
    danm_utils.check_host_interfaces(tenantnetwork_properties)

    # cleanup after ourselves
    danm_utils.delete_resources_by_manifest_path("/tmp/tenantnetwork-test/templates")
    # redeploy the default TenantConfig 'danm-tenant-config' after we finish
    execute.execute_unix_command("kubectl create -f /var/lib/docker/manifests/infra/danm-tenant-config.yaml")
    danm_utils.delete_resources_by_manifest_path("/tmp/tenantconfig-test/templates/tconf_07.yaml")


@robot_log
def replace_ifaces_in_fetched_chart_templates(path):
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_int_if }}/" + infra_int_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_ext_if }}/" + infra_ext_if + "/g' " + path)
    execute.execute_unix_command("sed -i 's/{{ .Values.infra_storage_if }}/" + infra_storage_if + "/g' " + path)
