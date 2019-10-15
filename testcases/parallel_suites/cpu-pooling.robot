*** Setting ***
Suite Setup       Set Basic Connection  ${cloudadmin}
Suite Teardown    Close All Connections

Library     ../../libraries/common/stack_infos.py
Library     ../../libraries/common/execute_command.py
Variables   ../../libraries/common/users.py

Library     ../cpu_pooling/tc_001_cpu_pool_validation_tests.py
Library     ../cpu_pooling/tc_002_exclusive_pool_tests.py
Library     ../cpu_pooling/tc_003_exclusive_pool_tests_more_cpu.py
Library     ../cpu_pooling/tc_004_shared_cpu_pool_tests.py

Test Timeout    10 minutes

*** Test Cases ***
CAAS_DPDK_CPU_001
    [Documentation]    TC 001 CPU Pool Validation Tests
    [Tags]    CI    VM    BM
    tc_001_cpu_pool_validation_tests

CAAS_DPDK_CPU_002
    [Documentation]    TC 002 Exclusive CPU Pool Tests
    [Tags]    CI    VM    BM
    tc_002_exclusive_pool_tests

CAAS_DPDK_CPU_003
    [Documentation]    TC 003 Exclusive CPU Pool Tests More CPU
    [Tags]    CI    BM
    tc_003_exclusive_pool_tests_more_cpu

CAAS_DPDK_CPU_004
    [Documentation]    TC 004 Shared CPU Pool Tests
    [Tags]    CI    VM    BM
    tc_004_shared_cpu_pool_tests