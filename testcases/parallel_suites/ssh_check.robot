*** Setting ***
Suite Setup    Set Basic Connection  ${cloudadmin}
Suite Teardown    Close All Connections

Library     ../../libraries/common/stack_infos.py
Library     ../../libraries/common/execute_command.py
Variables   ../../libraries/common/users.py

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
CAAS_BASIC_FUNC_001
    [Documentation]    TC 008 Storage Check
    [Tags]    CI
    [Timeout]    20 minutes
    tc_008_storage_check

CAAS_BASIC_FUNC_002
    [Documentation]    TC 002 pod health check
    [Tags]    CI
    [Timeout]    5 minutes
    tc_002_pod_health_check

CAAS_BASIC_FUNC_003
    [Documentation]    TC 003 test_registry
    [Tags]    CI
    tc_003_test_registry

CAAS_BASIC_FUNC_004
    [Documentation]    TC 004 SSH file check
    [Tags]    CI
    tc_004_ssh_file_check

CAAS_BASIC_FUNC_005
    [Documentation]    TC 005 SSH DNS server check
    [Tags]    CI
    tc_005_ssh_dns_server_check

CAAS_BASIC_FUNC_006
    [Documentation]    TC 006 SSH Test Ext Ntp
    [Tags]    CI
    tc_006_ssh_test_ext_ntp

CAAS_BASIC_FUNC_007
    [Documentation]    TC 007 SSH Test Overlay Quota
    [Tags]    CI
    tc_007_ssh_test_overlay_quota

CAAS_FLUENTD_001
    [Documentation]    TC 001 ssh test fluentd logging
    [Tags]    CI
    tc_001_ssh_test_fluentd_logging
