# Copyright 2019 AT&T
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

Creating Namespace
    ${search}=     set variable    namespace/test-ns created
    ${command}=    set variable    kubectl create namespace test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Creating the pod to specific namespace
    ${search}=     set variable    pod/my-pod created
    ${command}=    set variable    kubectl run --generator=run-pod/v1 my-pod --image=nginx --port=80 --namespace=test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Checking the pod whether the specific namespace created or not
    ${command}=    set variable    kubectl describe pod my-pod -n test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    test-ns

Delete the pod
    ${search}=     set variable    pod "my-pod" deleted
    ${command}=    set variable    kubectl delete pod my-pod -n test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Delete namespace
    ${search}=     set variable    namespace "test-ns" deleted
    ${command}=    set variable    kubectl delete namespace test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

*** Test Cases ***

Test to create Namespace
    Creating Namespace
Test to create the pod to specific namespace
    Creating the pod to specific namespace
Test to check the pod whether the specific namespace created or not
    Checking the pod whether the specific namespace created or not
Test to delete the pod
    Delete the pod
Test to delete namespace
    Delete namespace
