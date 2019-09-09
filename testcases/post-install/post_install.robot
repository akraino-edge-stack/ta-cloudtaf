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
Testing Deployment
    ${search}=     set variable    log_installation_success Installation complete, Installation Succeeded
    ${command}=    set variable    tail -n 1 /srv/deployment/log/bootstrap.log
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Testing Docker
    ${search}=     set variable    Docker version 19.03.2
    ${command}=    set variable    docker --version
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Testing Kubernetes Cluster
    ${command}=    set variable    kubectl get po --no-headers --namespace=kube-system --field-selector status.phase!=Running 2> /dev/null
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should be empty    ${out}

Testing State Services
    Test Service State    docker.service
    Test Service State    kubelet.service

Test Service State
    [Arguments]   ${service}
    ${running}=    set variable    running
    ${active}=    set variable    active
    ${command1}=    set variable    systemctl show -p SubState ${service} | sed 's/SubState=//g'
    ${command2}=    set variable    systemctl show -p ActiveState ${service} | sed 's/ActiveState=//g'
    ${out1}=    ssh.Execute Command    ${command1}    controller-1
    ${out2}=    ssh.Execute Command    ${command2}    controller-1
    log    ${out1}
    log    ${out2}
    Should contain    ${out1}    ${running}
    Should contain    ${out2}    ${active}

Testing Node
    ${count1}=    get length    ${ALL_MASTERS_IN_SYSTEM}
    ${count2}=    get length    ${ALL_PURE_WORKERS_IN_SYSTEM}
    ${total}=     evaluate   ${count1}+${count2}
    ${command}=    set variable    kubectl get no --no-headers | grep Ready | grep -v SchedulingDisabled | wc -l
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should be equal as integers    ${out}    ${total}

Testing Package Manager Status
    ${docker_image}=     set variable    docker images -f \'reference=*/caas/hyperkube\' --format=\"{{.Repository}}:{{.Tag}}\"
    ${out1}=    ssh.Execute Command    ${docker_image}    controller-1
    ${image_pull}=    set variable    docker pull ${out1} | grep -i status
    ${out2}=    ssh.Execute Command    ${image_pull}    controller-1
    ${uptodate}=    set variable    Status: Image is up to date for ${out1}
    ${out3}=    ssh.Execute Command    ${image_pull}    controller-1
    log    ${out3}
    Should be equal    ${out3}    ${uptodate}

Testing Helm Caas infra Status

    ${search}=     set variable    STATUS: DEPLOYED
    ${command}=    set variable    helm status caas-infra --kube-context string | grep STATUS:
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should be equal    ${out}    ${search}


*** Test Cases ***
Verify Deployment
    Testing Deployment
Verify Docker Version
    Testing Docker
Verify Kubernetes Clusters
    Testing Kubernetes Cluster
Verify State of required services
    Testing State Services
Verify Node Functionality
    Testing Node
Verify Package Manager Status
    Testing Package Manager Status
Verify Helm Caas Infra Status
    Testing Helm Caas infra Status
