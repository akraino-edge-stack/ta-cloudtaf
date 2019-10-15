*** Settings ***
Suite Setup       Set Basic Connection    ${cloudadmin}
Suite Teardown    Close All Connections

Library           ../../libraries/common/stack_infos.py
Library           ../../libraries/common/execute_command.py
Variables         ../../libraries/common/users.py

Library           ../HPA_check/HPA_check.py
Library           ../HPA_check/Custom_HPA_check.py


*** Test Cases ***
CAAS_ELASTICITY_001
    [Documentation]    HPA check
    [Tags]   hpa    CI    Release    VM    BM
    [Timeout]    7 minutes
    HPA_check

CAAS_ELASTICITY_002
    [Documentation]    Custom HPA check
    [Tags]   hpa    CI    Release    VM    BM
    [Timeout]    9 minutes
    Custom_HPA_check
