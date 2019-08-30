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

Creating pod
    ${search}=     set variable    pod/my-pod created
    ${command}=    set variable    kubectl run --generator=run-pod/v1 my-pod --image=nginx --port=80 --labels="name=mypod"
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Creating kubernetes service with type NodePort
    ${search}=     set variable    service/my-service created
    ${command}=    set variable    kubectl create -f service.yaml --validate=false
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Getting the Node IP of the pod
    ${command}=    set variable    kubectl get pods --all-namespaces -o wide | grep my-pod | awk '{ print $8 }'
    ${output}=    ssh.Execute Command    ${command}    controller-1
    log    ${output}
    ${ip_address}=  Set Variable ${output}

Testing the service
    ${search}=     set variable    Welcome to nginx!
    ${command}=    set variable    curl http://${ip_address}:32456
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Delete the pod
    ${search}=     set variable    pod "my-pod" deleted
    ${command}=    set variable    kubectl delete pod my-pod 
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Delete the service
    ${search}=     set variable    service "my-service" deleted
    ${command}=    set variable    kubectl delete service my-service
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

*** Test Cases ***
Verify creating and testing services
    Creating pod
    Creating kubernetes service with type NodePort
    Getting the Node IP of the pod
    Testing the service
    Delete the pod
    Delete the service
