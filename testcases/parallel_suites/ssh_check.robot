*** Setting ***
Suite Setup    Set Basic Connection  ${cloudadmin}
Suite Teardown    Close All Connections

Library     ../../libraries/common/stack_infos.py
Library     ../../libraries/common/execute_command.py
Variables   ../../libraries/common/users.py

Library     ../basic_func_tests/tc_001_ssh_ncir_vnf_installer_check.py
Library     ../basic_func_tests/tc_002_pod_health_check.py
Library     ../basic_func_tests/tc_003_test_registry.py
Library     ../basic_func_tests/tc_004_ssh_file_check.py
Library     ../basic_func_tests/tc_005_ssh_dns_server_check.py
Library     ../basic_func_tests/tc_006_ssh_test_ext_ntp.py
Library     ../basic_func_tests/tc_007_ssh_test_overlay_quota.py
Library     ../fluentd/tc_001_ssh_test_fluentd_logging.py
Library     ../fluentd/tc_002_elasticsearch_storage_check.py
Library     ../basic_func_tests/tc_008_storage_check.py


Test Timeout    3 minutes

*** Test Cases ***
NCI_R_CAAS_BASIC_FUNC_001
    [Documentation]    TC 001 NCIR VNF Installer Check
    [Tags]    CI    Release    VM
    tc_001_ssh_ncir_vnf_installer_check

NCI_R_CAAS_BASIC_FUNC_002
    [Documentation]    TC 002 pod health check
    [Tags]    CI    Release    VM    BM
    [Timeout]    5 minutes
    tc_002_pod_health_check

NCI_R_CAAS_BASIC_FUNC_003
    [Documentation]    TC 003 test_registry
    [Tags]    CI    Release    VM    BM
    tc_003_test_registry

NCI_R_CAAS_BASIC_FUNC_004
    [Documentation]    TC 004 SSH file check
    [Tags]    CI    Release    VM    BM
    tc_004_ssh_file_check

NCI_R_CAAS_BASIC_FUNC_005
    [Documentation]    TC 005 SSH DNS server check
    [Tags]    CI    Release    VM    BM
    tc_005_ssh_dns_server_check

NCI_R_CAAS_BASIC_FUNC_006
    [Documentation]    TC 006 SSH Test Ext Ntp
    [Tags]    CI    Release    VM    BM
    tc_006_ssh_test_ext_ntp

NCI_R_CAAS_BASIC_FUNC_007
    [Documentation]    TC 007 SSH Test Overlay Quota
    [Tags]    CI    Release    VM    BM
    tc_007_ssh_test_overlay_quota

NCI_R_CAAS_BASIC_FUNC_008
    [Documentation]    TC 008 Storage Check
    [Tags]    Release    CI    VM    BM
    [Timeout]    20 minutes
    tc_008_storage_check

NCI_R_CAAS_FLUENTD_001
    [Documentation]    TC 001 ssh test fluentd logging
    [Tags]    CI   Release   fluentd    VM    BM
    tc_001_ssh_test_fluentd_logging

NCI_R_CAAS_FLUENTD_002
    [Documentation]    TC 002 elasticsearch storage check
    [Tags]    CI   Release   fluentd   elastic    VM
    tc_002_elasticsearch_storage_check
