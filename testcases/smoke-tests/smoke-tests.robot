# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

*** Settings ***
Library             Collections
Library             cluster.cluster.Cluster    WITH NAME    Cluster
Library             crl.remotesession.remotesession.RemoteSession
...                 WITH NAME    RemoteSession
Resource            ssh.robot
Test Setup          ssh.Setup Connections

*** Keywords ***

Validate Cluster

    :FOR    ${node}     IN      @{ALL_MASTERS_IN_SYSTEM}
    \    ${output}=     Ssh.Execute Command     hostname      ${node}
    \    Should Be Equal    ${node}    ${output}

    :FOR    ${node}     IN      @{ALL_PURE_WORKERS_IN_SYSTEM}
    \    ${output}=     Ssh.Execute Command     hostname      ${node}
    \    Should Be Equal    ${node}    ${output}

    :FOR    ${node}     IN      @{ALL_PURE_STORAGES_IN_SYSTEM}
    \    ${output}=     Ssh.Execute Command     hostname      ${node}
    \    Should Be Equal    ${node}    ${output}

    ${hosts}=   Cluster.Get Hosts
    :FOR  ${node}      IN       @{hosts}
    \    ${output}=     Ssh.Execute Command     hostname      ${node.name}
    \    Should Be Equal    ${node.name}    ${output}

    ${masters_len}=  Get Length    ${ALL_MASTERS_IN_SYSTEM}

    Should Be True    ${masters_len} == 3
    ...   Number of masters should be 3 not ${masters_len}
    Verify Database

Reboot Management VIP Node
    RemoteSession.Execute Background Command In Target    sleep 1; reboot
    ...    target=sudo-default
    Sleep    1
    RemoteSession.Close
    ssh.Setup Connections

Stop Database
    [Arguments]    ${node}
    ${result}=    RemoteSession.Execute Command In Target
    ...    systemctl stop mariadb.service    ${node}
    Should Be Equal   ${result.status}    0    ${result.stderr}

Start Database
    [Arguments]    ${node}
    ${result}=    RemoteSession.Execute Command In Target
    ...    systemctl start mariadb.service    ${node}
    Should Be Equal   ${result.status}    0    ${result.stderr}

Verify Database
    [Arguments]    ${node}=sudo-default    ${expected_cluster_size}=3
    ${out}=    ssh.Execute Command    mysql <<< "show status like 'wsrep_cluster_size';"
    ...    ${node}
    Should match     ${out}     *wsrep_cluster_size*${expected_cluster_size}*

*** Test Cases ***

Verify Cluster Config Management
    Validate Cluster

Verify Cluster Config Management After Reboot Management VIP Node
    Reboot Management VIP Node
    Wait Until Keyword Succeeds    600s    1s     Validate Cluster

Verify Database Stop And Start
    ${first_master}=    Collections.Get From List    ${ALL_MASTERS_IN_SYSTEM}    0
    Stop Database    sudo-${first_master}
    Wait Until Keyword Succeeds    6x    18s    Verify Database    sudo-${first_master}
    ...    expected_cluster_size=2
    Start Database    sudo-${first_master}
    Wait Until Keyword Succeeds    6x    18s    Verify Database    sudo-${first_master}

Verify Create All And No Roles
    [Documentation]    Verify no_roles and all_roles user creation
    ${all_roles}=    Cluster.Create User With Roles    all_roles
    Log    ${all_roles}
    ${no_roles}=    Cluster.Create User With Roles    no_roles
    Log    ${no_roles}

Verify SudoShells
    [Documentation]    Test SudoShells
    ${hosts}=   Cluster.Get Hosts
    :FOR  ${node}      IN       @{hosts}
    \     ${result}=     RemoteSession.Execute Command In Target   whoami
    \     ...    target=sudo-${node.name}
    \     Should Be Equal    ${result.stdout}    root

    ${result}=    RemoteSession.Execute Command In Target   whoami
    ...    target=sudo-default
    Should Be Equal     ${result.stdout}     root

Verify Remotescript Default
    [Documentation]    test target remotescript-default
    ${result}=    RemoteSession.Execute Command In Target   echo -n out
    ...    target=remotescript-default
    Should Be Equal    ${result.stdout}    out
