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
Test Setup          Run Keywords
...                 ssh.Setup Connections
...                 Create Namespace
Test Teardown       Run Keywords
...                 Delete Namespace

*** Keywords ***

Create Namespace
    ${command}=    set variable    kubectl create namespace test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    namespace/test-ns created
    
Create pod in specific namespace
    ${command}=    set variable    kubectl run --generator=run-pod/v1 my-pod --image=nginx --port=80 --namespace=test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    pod/my-pod created

Check whether pod was created in specific namespace
    ${command}=    set variable    kubectl describe pod my-pod -n test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    test-ns

Delete pod
    ${command}=    set variable    kubectl delete pod my-pod -n test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    pod "my-pod" deleted

Delete Namespace
    ${command}=    set variable    kubectl delete namespace test-ns
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    namespace "test-ns" deleted

*** Test Cases ***

Verify creating and testing Namespaces
    Create pod in specific namespace
    Check whether pod was created in specific namespace
    Delete pod
