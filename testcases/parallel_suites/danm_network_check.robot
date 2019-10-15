*** Setting ***
Suite Setup    Set Basic Connection  ${cloudadmin}
Suite Teardown    Close All Connections

Library     ../../libraries/common/stack_infos.py
Library     ../../libraries/common/execute_command.py
Variables   ../../libraries/common/users.py

Library     ../danm_network_check/tc_001_danmnet_object_check.py
Library     ../danm_network_check/tc_002_tenantnetwork_pod_check.py
Library     ../danm_network_check/tc_003_clusternetwork_pod_check.py

Test Timeout    12 minutes

*** Test Cases ***
CAAS_DANM_001
    [Documentation]    TC 001 Danmnet Check
    [Tags]    CI    VM    BM    Release
    tc_001_danmnet_object_check

CAAS_DANM_002
    [Documentation]    TC 002 Tenantnetwork Pod Check
    [Tags]    CI    VM    BM    Release
    tc_002_tenantnetwork_pod_check

CAAS_DANM_003
    [Documentation]    TC 003 Clusternetwork Pod Check
    [Tags]    CI    VM    BM    Release
    tc_003_clusternetwork_pod_check