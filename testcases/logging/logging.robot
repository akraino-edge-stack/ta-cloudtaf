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

*** Keywords ***
Testing Expected API Server PODs
    ${apiserver_pod_count}=     set variable    1
    ${apiserver_pods_command}=    set variable    kubectl get pods --all-namespaces | grep custom-metrics-apiserver- | wc -l
    ${out}=    ssh.Execute Command    ${apiserver_pods_command}    controller-1
    Log    apiserver_pods_command result: ${out}
    Should Be Equal     ${out}     ${apiserver_pod_count}


Testing Expected Elasticsearch-data PODs
    ${elastic_db_pod_count}=     set variable    3
    ${elastic_db_pod_command}=    set variable    kubectl get pods --all-namespaces | grep elasticsearch-data- | wc -l
    ${out}=    ssh.Execute Command    ${elastic_db_pod_command}    controller-1
    Log    elastic_db_pod_command result: ${out}
    Should Be Equal     ${out}     ${elastic_db_pod_count}


Testing Expected Elasticsearch-master PODs
    ${expected_out}=     set variable    3
    ${command}=    set variable    kubectl get pods --all-namespaces | grep elasticsearch-master- | wc -l
    ${out}=    ssh.Execute Command    ${command}    controller-1
    Log    Elasticsearch-master result: ${out}
    Should Be Equal     ${out}     ${expected_out}


Testing Expected metrics-server PODs
    ${expected_out}=     set variable    1
    ${command}=    set variable    kubectl get pods --all-namespaces | grep metrics-server- | wc -l
    ${out}=    ssh.Execute Command    ${command}    controller-1
    Log    metrics-server result: ${out}
    Should Be Equal     ${out}     ${expected_out}


*** Test Cases ***
Verify Expected Pods
    Testing Expected API Server PODs
    Testing Expected Elasticsearch-data PODs
    Testing Expected Elasticsearch-master PODs
    Testing Expected metrics-server PODs
