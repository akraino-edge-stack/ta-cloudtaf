# Copyright 2019 ATT
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


*** Variables ***
${MAX_OFFSET}=    0.04


*** Keywords ***
Masters Offset
    :FOR    ${node}     IN      @{ALL_MASTERS_IN_SYSTEM}
    \    ${output}=     Execute Command     ntpq -p | grep "^[\*]" | awk '{print $9}'      ${node}
    \    Should Be True    ${output} < ${MAX_OFFSET}


Workers Offset for each Master
    :FOR    ${master}     IN      @{ALL_MASTERS_IN_SYSTEM}
    \    Worker Master Offset    ${master}

Worker Master Offset
    [Arguments]    ${master}
    :FOR    ${node}     IN      @{ALL_PURE_WORKERS_IN_SYSTEM}
    \    ${output}=     Execute Command      ntpq -p | grep ${master} | awk '{print $9}'    ${node}
    \    Should Be True    ${output} < ${MAX_OFFSET}


*** Test Cases ***
Verify Masters Offset
    Masters Offset
Verify Workers Offset for each Master
    Workers Offset for each Master