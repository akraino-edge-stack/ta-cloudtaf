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
...                 Copy artifacts to Target
...                 Create pod
...                 Create Kubernetes service with type NodePort
Test Teardown       Run Keywords
...                 Delete pod
...                 Delete service
...                 Cleanup artifacts, copied files, and images on Target

*** Variables ***

${test_base_dir}                testcases/kube-service
${service_yaml_name}            service.yaml
${image_name}                   registry.kube-system.svc.rec.io:5555/nginx:1.7
${artifacts}                    nginx.tar

*** Keywords ***

Copy artifacts to Target
    [Arguments]    ${node}=sudo-default
    ${pull_an_image}=   ssh.Execute command   docker pull nginx     ${node}
    ${save_image}=    set variable    docker save -o ${artifacts} nginx
    ${out}=    ssh.Execute Command    ${save_image}    ${node}
    ${load_image}=    set variable    docker load -i ${artifacts}
    ${out}=    ssh.Execute Command    ${load_image}    ${node}
    ${tag_image}=    ssh.Execute Command    docker tag nginx ${image_name}    ${node}
    ${push_image}=    ssh.Execute Command    docker push ${image_name}    ${node}

Create pod
    [Arguments]    ${node}=sudo-default
    ${search}=     set variable    pod/my-pod created
    ${command}=    set variable    kubectl run --generator=run-pod/v1 my-pod --image=${image_name} --port=80 --labels="name=mypod"
    ${out}=    ssh.Execute Command    ${command}    ${node}
    Sleep  30s
    log    ${out}
    Should contain    ${out}    ${search}

Create Kubernetes service with type NodePort
    [Arguments]    ${node}=sudo-default
    ${search}=     set variable    service/my-service created
    RemoteSession.Copy File To Target    ${test_base_dir}/${service_yaml_name}    target=${node}
    ${command}=    set variable    kubectl apply -f ${service_yaml_name}
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Get the Node IP of the pod and Port number of the service and Test the service
    ${command}=    set variable    kubectl get pods --all-namespaces -o wide | grep my-pod | awk '{ print $8 }'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${ip_address}=     set variable    ${result.stdout}
    Log    ip_address=${ip_address}
    ${command}=    set variable    kubectl get services | grep my-service | awk '{ print $5 }' | awk -F ':' '{print $2}' | tr -d /TCP
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${node_port}=     set variable    ${result.stdout}
    Log    node_port=${node_port}
    ${command}=    set variable    curl http://${ip_address}:${node_port}
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    Should Contain    ${result.stdout}    Welcome to nginx!

Delete pod
    [Arguments]    ${node}=sudo-default
    ${search}=     set variable    pod "my-pod" deleted
    ${command}=    set variable    kubectl delete pod my-pod
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Delete service
    [Arguments]    ${node}=sudo-default
    ${search}=     set variable    service "my-service" deleted
    ${command}=    set variable    kubectl delete service my-service
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Cleanup artifacts, copied files, and images on Target
   [Arguments]    ${node}=sudo-default
   ${cleanup_copied_files}=    ssh.Execute Command    rm -rf ${service_yaml_name}    ${node}
   ${remove_images}=    set variable    docker image rm nginx | docker rmi ${image_name}
   ${out}=    ssh.Execute Command    ${remove_images}    ${node}
   ${remove_artifacts}=    ssh.Execute Command    rm -rf ${artifacts}    ${node}

*** Test Cases ***
Verify creating and testing services
    Get the Node IP of the pod and Port number of the service and Test the service
