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
    ${out}=    Execute Command    ${apiserver_pods_command}    controller-1
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


Testing Elasticsearch Cluster Statistics
    ${command}=    set variable    curl -v --user elastic:changeme 'elasticsearch-logging.kube-system.svc.rec.io:9200/_cluster/stats?human&pretty'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Be Equal    ${result.status}    0


Testing Elasticsearch Database Details
    ${expected_out}=     set variable    elasticsearch-data-
    ${command}=    set variable    curl --user elastic:changeme 'elasticsearch-logging.kube-system.svc.rec.io:9200/_cat/allocation?human&pretty'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


Testing specific cluster statistic
    ${expected_out}=     set variable    max_uptime_in_millis
    ${command}=    set variable    curl --user elastic:changeme 'elasticsearch-logging.kube-system.svc.rec.io:9200/_cluster/stats?&filter_path=nodes.jvm.max_uptime_in_millis&format=yaml'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


Testing Elasticsearch Indice Mapping
    ${command}=    set variable    curl --user elastic:changeme 'elasticsearch-logging.kube-system.svc.rec.io:9200/_cat/indices?v' | grep open | awk '{print $3}'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${expected_out}=     set variable    ${result.stdout}
    Log    index=${expected_out}
    ${command}=    set variable    curl --user elastic:changeme "elasticsearch-logging.kube-system.svc.rec.io:9200/${expected_out}/_mapping/?format=yaml"
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    ${expected_out}


Testing Prometheus logs
    ${command}=    set variable    kubectl get pods --all-namespaces | grep prometheus- | awk '{print $2}'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${prometheus_pod_name}=     set variable    ${result.stdout}
    Log    prometheus_pod_name=${prometheus_pod_name}
    ${command}=    set variable    kubectl logs -n kube-system ${prometheus_pod_name} | grep 'WAL checkpoint complete'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    WAL checkpoint complete


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
Verify Prometheus logs
    Testing Prometheus logs
