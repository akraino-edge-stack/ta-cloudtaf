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

Logging into Docker Registry

    ${search}=     set variable    Login Succeeded
    ${command}=    set variable    cat /home/cloudadmin/password.txt | docker login --username admin --password-stdin registry.kube-system.svc.rec.io:5555
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    Should contain    ${out}    ${search}

Push an image to docker registry

    ${search}=     set variable    Pushed
    ${command}=    set variable    docker push registry.kube-system.svc.rec.io:5555/hello-world
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    Should contain    ${out}    ${search}

Pull an image from docker registry

    ${search}=     set variable    Pull complete
    ${command}=    set variable    docker pull registry.kube-system.svc.rec.io:5555/hello-world
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    Should contain    ${out}    ${search}

Delete an image from Docker registry

    ${search}=     set variable    Deleted
    ${command}=    set variable    docker image rm -f registry.kube-system.svc.rec.io:5555/hello-world
    ${out}=    RemoteSession.Execute Command In Target    ${command}
    Should contain    ${out}    ${search}

*** Test Cases ***

Verify Docker registry
    Logging into Docker Registry
    Push an image to docker registry
    Pull an image from docker registry
    Delete an image from Docker registry
