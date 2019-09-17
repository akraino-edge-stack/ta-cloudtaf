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
Test Teardown       Run Keywords
...                 Delete docker image from Docker registry

*** Variables ***
${docker_image_name}            registry.kube-system.svc.rec.io:5555/hello-world
${docker_image_tag}             1.1
${docker_image}                 ${docker_image_name}:${docker_image_tag}
${artifacts}                    hello-world.tar

*** Keywords ***

Copy artifacts to Target
    ${pull_an_image}=    RemoteSession.Execute Command In Target    docker pull hello-world
    ${save_image}=    set variable    docker save -o ${artifacts} hello-world
    ${out}=    ssh.Execute Command    ${save_image}    controller-1
#   RemoteSession.Copy File To Target    ${test_base_dir}/hello-world.tar    target=controller-1
    ${load_image}=    set variable    docker load -i ${artifacts}
    ${out}=    ssh.Execute Command    ${load_image}    controller-1
    log    ${out}
    ${Tag_docker_image}=    ssh.Execute Command    docker tag hello-world ${docker_image}    controller-1
    log    ${Tag_docker_image}

Push docker image from docker registry
    ${command}=    set variable    docker push ${docker_image}
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    log    ${out}

Remove images and artifacts from node's localhost
    ${command}=    set variable    docker rmi hello-world
    ${out}=    ssh.Execute Command    ${command}  controller-1
    log    ${out}    
    ${command}=    set variable    docker rmi ${docker_image}
    ${out}=    ssh.Execute Command    ${command}  controller-1
    log    ${out}
    ${remove_artifacts}=    ssh.Execute Command    rm -rf ${artifacts}    controller-1

Pull docker image from docker registry
    ${command}=    set variable    docker pull ${docker_image}
    ${out}=    ssh.Execute Command    ${command}  controller-1
    log    ${out}
    Should contain    ${out}   Pull complete  

Delete docker image from Docker registry
    ${command}=    set variable    docker images --digests | grep ${docker_image_name} | awk $'{print ($3)}'
    ${result}=    RemoteSession.Execute Command In Target    ${command}
    ${digest_number}=     set variable    ${result.stdout}
    log    digest_number=${digest_number}
    ${command}=    set variable    curl -k -v --cert /etc/docker-registry/registry1.pem --key /etc/docker-registry/registry1-key.pem -X DELETE https://registry.kube-system.svc.rec.io:5555/v2/hello-world/manifests/${digest_number}
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    log    ${out}
    Should contain    ${out}   202 Accepted

*** Test Cases ***

Verify Docker registry
    Push docker image from docker registry
    Remove images and artifacts from node's localhost
    Pull docker image from docker registry
