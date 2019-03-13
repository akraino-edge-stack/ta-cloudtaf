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

Library             cluster.cluster.Cluster   WITH NAME   Cluster
Library             crl.remotesession.remotesession.RemoteSession
                    ...    WITH NAME    RemoteSession
Suite Setup         Setup Suite
Suite Teardown      Teardown Suite

*** Keywords ***

Setup Suite
    ${master}=    Get Variable Value    ${RFCLI_TARGET_1.MASTER_PROFILE}    caas_master
    ${worker}=    Get Variable Value    ${RFCLI_TARGET_1.WORKER_PROFILE}    caas_worker
    Cluster.Set Profiles    master=${master}     worker=${worker}

Teardown Suite
    Run Keyword And Ignore Error    Cluster.Delete Users
    RemoteSession.Close
