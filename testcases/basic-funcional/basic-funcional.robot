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
Testing DNS Service
    ${search}=     set variable    3 packets transmitted, 3 packets received, 0% packet loss
    ${command}=    set variable    kubectl apply -f https://k8s.io/examples/application/deployment.yaml
    ${create_deployment_out}=    ssh.Execute Command    ${command}    controller-1
    log    ${create_deployment_out}
    ${command_get_pod}=        set variable    kubectl get pods | grep Running | awk '{print $1}' | sed -n 1p
    ${pod_out}=    ssh.Execute Command    ${command_get_pod}    controller-1
    log    ${pod_out} is one among the running pods
    ${command_ping}=        set variable    kubectl exec -it ${pod_out} -- ping -c 3 www.google.com
    ${out}=    ssh.Execute Command    ${command_ping}    controller-1
    Should contain    ${out}    ${search}
    ${cleanup}=    set variable    kubectl apply -f https://k8s.io/examples/application/deployment.yaml
    ssh.Execute Command    ${cleanup}    controller-1


*** Test Cases ***
Verify DNS Service
    Testing DNS Service
