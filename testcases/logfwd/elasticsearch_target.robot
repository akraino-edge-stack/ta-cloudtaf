##############################################################################
# Copyright (c) 2019 AT&T Intellectual Property.                             #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License.                   #
#                                                                            #
# You may obtain a copy of the License at                                    #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT  #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.           #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
##############################################################################

*** Settings ***
Library             Collections
Library             cluster.cluster.Cluster    WITH NAME    Cluster
Library             crl.remotesession.remotesession.RemoteSession
...                 WITH NAME    RemoteSession
Resource            ssh.robot
Test Setup          ssh.Setup Connections
*** Variables ***
${ELASTIC_ENDPOINT}    http://elasticsearch-logging.kube-system.svc.rec.io:9200



*** Keywords ***
Testing Expected API Server PODs
    ${apiserver_pod_count}=     set variable    1
    ${apiserver_pods_command}=    set variable    kubectl get pods -n kube-system --field-selector=status.phase==Running | grep custom-metrics-apiserver- | wc -l
    ${result}=    RemoteSession.Execute Command In Target    ${apiserver_pods_command}
    Log    apiserver_pods_command result: ${result.stdout}
    Should Be Equal     ${result.stdout}     ${apiserver_pod_count}


Testing Expected Elasticsearch-data PODs
    ${elastic_db_pod_count}=     set variable    3
    ${elastic_db_pod_command}=    set variable    kubectl get pods -n kube-system --field-selector=status.phase==Running | grep elasticsearch-data- | wc -l
    ${result}=    RemoteSession.Execute Command In Target    ${elastic_db_pod_command}
    Log    elastic_db_pod_command result: ${result.stdout}
    Should Be Equal     ${result.stdout}     ${elastic_db_pod_count}


Testing Expected Elasticsearch-master PODs
    ${expected_out}=     set variable    3
    ${command}=    set variable    kubectl get pods -n kube-system --field-selector=status.phase==Running | grep elasticsearch-master- | wc -l
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Log    Elasticsearch-master result: ${result.stdout}
    Should Be Equal     ${result.stdout}     ${expected_out}


Testing Expected metrics-server PODs
    ${expected_out}=     set variable    1
    ${command}=    set variable    kubectl get pods -n kube-system --field-selector=status.phase==Running | grep metrics-server- | wc -l
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Log    metrics-server result: ${result.stdout}
    Should Be Equal     ${result.stdout}     ${expected_out}


Testing Elasticsearch Cluster Statistics
    ${command}=    set variable    curl '${ELASTIC_ENDPOINT}/_cluster/stats' | jq -r '.status'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Be Equal    ${result.status}    0
    Should Be Equal    ${result.stdout}    green


Testing Elasticsearch Database Details
    ${expected_out}=     set variable    elasticsearch-data-
    ${command}=    set variable    curl '${ELASTIC_ENDPOINT}/_cat/allocation?human&pretty'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


Testing specific cluster statistic
    ${expected_out}=     set variable    max_uptime_in_millis
    ${command}=    set variable    curl '${ELASTIC_ENDPOINT}/_cluster/stats?&filter_path=nodes.jvm.max_uptime_in_millis&format=yaml'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


Testing Elasticsearch Indice Mapping
    ${command}=    set variable    curl '${ELASTIC_ENDPOINT}/_cat/indices?v' 2>&1 | grep "green\s*open" | awk 'NR==1 {print $3}'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${expected_out}=     set variable    ${result.stdout}
    Log    index=${expected_out}
    ${command}=    set variable    curl "${ELASTIC_ENDPOINT}/${expected_out}/_mapping/?format=yaml"
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


*** Test Cases ***
Verify Expected Pods
    Testing Expected API Server PODs
    Testing Expected Elasticsearch-data PODs
    Testing Expected Elasticsearch-master PODs
    Testing Expected metrics-server PODs
Verify Elasticsearch Cluster Statistics
    Testing Elasticsearch Cluster Statistics
Verify Elasticsearch Database Details
    Testing Elasticsearch Database Details
Verify specific cluster statistic
    Testing specific cluster statistic
Verify Elasticsearch Indice Mapping
    Testing Elasticsearch Indice Mapping
