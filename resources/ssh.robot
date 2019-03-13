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
Documentation     Defines targets to RemoteSession - library
...               'default' points to the active master via infra_external like
...               the connections to the caas_master - nodes.
...               Connection to the other nodes(caas_worker, storage) are done infra_internal
...               via the active master. (in case the controller is also a storage the
...               direct connection is used instead).

Library        crl.remotesession.remotesession.RemoteSession
...            WITH NAME    RemoteSession
Library        cluster.cluster.Cluster
...   WITH NAME  Cluster

*** Variables ***
@{ALL_MASTERS_IN_SYSTEM}              @{EMPTY}
@{ALL_PURE_WORKERS_IN_SYSTEM}         @{EMPTY}
@{ALL_PURE_STORAGES_IN_SYSTEM}        @{EMPTY}
${IS_DPDK_IN_USE}                     ${False}

*** Keywords ***

Setup Connections
    [Documentation]     Setup targets for the RemoteSession Library for
    ...                 for all nodes.

    Cluster.Initialize  host=${RFCLI_TARGET_1.IP}
    ...                 user=${RFCLI_TARGET_1.USER}
    ...                 password=${RFCLI_TARGET_1.PASS}

    ${remotesession}=  Get Library Instance    RemoteSession

    Cluster.Initialize RemoteSession   ${remotesession}
    ${master}=    Get Variable Value    ${RFCLI_TARGET_1.MASTER_PROFILE}    caas_master
    ${worker}=    Get Variable Value    ${RFCLI_TARGET_1.WORKER_PROFILE}    caas_worker

    ${masters}=    Cluster.Get Hosts Containing   ${master}
    Set Global Variable     ${ALL_MASTERS_IN_SYSTEM}     ${masters}

    ${pure_storages}=    Cluster.Get Hosts With Profiles    storage
    Set Global Variable     ${ALL_PURE_STORAGES_IN_SYSTEM}     ${pure_storages}

    ${pure_workers}=    Cluster.Get Hosts With Profiles    ${worker}
    Set Global Variable     ${ALL_PURE_WORKERS_IN_SYSTEM}     ${pure_workers}

    ${is_dpdk_in_use}=  Cluster.Is Dpdk
    Set Global Variable  ${IS_DPDK_IN_USE}  ${is_dpdk_in_use}


Execute Command
    [Arguments]     ${CMD}      ${NODE_NAME}=default    ${CHECK_STDERR}=${True}
    ${result}=     RemoteSession.Execute Command In Target     ${CMD}  target=${NODE_NAME}
    Should Be Equal As Integers     ${result.status}       0    ${result.stderr}
    Run Keyword If    ${CHECK_STDERR}    Should Be Empty    ${result.stderr}
    [Return]    ${result.stdout}

