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
...                 Create Pod with readiness probe
Test Teardown       Run Keywords
...                 Delete pod and copied files on Target node

*** Variables ***

${test_base_dir}                testcases/pod-health-check
${readiness_probe_yaml_name}    readiness-probe.yaml
${image_name}                   registry.kube-system.svc.rec.io:5555/alpine:1.7
${artifacts}                    alpine.tar

*** Keywords ***

Copy artifacts to Target
    [Arguments]         ${node}=sudo-default
    ${pull_an_image}=   ssh.Execute command   docker pull alpine     ${node}
    ${save_image}=    set variable    docker save -o ${artifacts} alpine
    ${out}=    ssh.Execute Command    ${save_image}    ${node}
    ${load_image}=    set variable    docker load -i ${artifacts}
    ${out}=    ssh.Execute Command    ${load_image}    ${node}
    log    ${out}
    ${Tag_an_image}=    ssh.Execute Command    docker tag alpine ${image_name}    ${node}
    ${push_an_image}=    ssh.Execute Command    docker push ${image_name}    ${node}

Create Pod with readiness probe
    [Arguments]         ${node}=sudo-default
    ${search}=     set variable    deployment.apps/readiness-deployment created
    RemoteSession.Copy File To Target    ${test_base_dir}/${readiness_probe_yaml_name}    target=${node}
    ${command}=    set variable    kubectl apply -f ${readiness_probe_yaml_name}
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Check created pods are in running state or not
    [Arguments]         ${node}=sudo-default
    ${search}=     set variable    Running
    Sleep   30s
    ${command}=    set variable    kubectl get pods -l app=readiness-deployment
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Confirm all the replicas are in available state
    [Arguments]         ${node}=sudo-default
    ${search}=     set variable    3 desired | 3 updated | 3 total | 3 available | 0 unavailable
    ${command}=    set variable    kubectl describe deployment readiness-deployment | grep Replicas:
    ${out}=    ssh.Execute Command    ${command}    ${node}
    log    ${out}
    Should contain    ${out}    ${search}

Introduce a Failure
    [Arguments]         ${node}=sudo-default
    ${get_pod}=    ssh.Execute Command    kubectl get pods | grep readiness | awk '{ print $1 }'    ${node}
    ${out}=    ssh.Execute Command    kubectl exec -it ${get_pods} -- rm /tmp/healthy    ${node}
    log    ${out}
    ${pod_status}=    ssh.Execute Command    kubectl get pods -l app=readiness-deployment   ${node}
    log    ${pod_status}
    Should contain    ${pods_status}    0/1
    ${check_replicas}=    ssh.Execute Command    kubectl describe deployment readiness-deployment | grep Replicas:    ${node}
    log    ${check_replicas}
    Should contain    ${check_replicas}    3 desired | 3 updated | 3 total | 2 available | 1 unavailable
    ${restore_pod_status}=    ssh.Execute Command    kubectl exec -it ${get_pods} -- touch /tmp/healthy    ${node}
    log    ${restore_pod_status}

Check all the pods in running state
    [Arguments]         ${node}=sudo-default
    ${out}=    ssh.Execute Command   kubectl get pods -l app=readiness-deployment    ${node}
    log    ${out}
    Should contain    ${out}    Running

Delete pod and copied files on Target node
   [Arguments]         ${node}=sudo-default
   ${delete_pod}=    ssh.Execute Command   kubectl delete -f ${readiness_probe_yaml_name}    ${node}
   log    ${delete_pod}
   Should contain    ${delete_pod}    deployment.apps "readiness-deployment" deleted
   ${cleanup_copied_files}=    ssh.Execute Command    rm -rf ${readiness_probe_yaml_name}    ${node}
   ${remove_images}=    set variable    docker image rm alpine | docker rmi ${image_name}
   ${out}=    ssh.Execute Command    ${remove_images}    ${node}
   ${remove_artifacts}=    ssh.Execute Command    rm -rf ${artifacts}    ${node}

*** Test Cases ***

Verify Pod Health Check
    Check created pods are in running state or not
    Confirm all the replicas are in available state
    Introduce a Failure
    Check all the pods in running state
