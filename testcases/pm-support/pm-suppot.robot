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

*** Variables ***
${docker_image_name}            registry.kube-system.svc.rec.io:5555/custom_metrics_test
${docker_image_tag}             0.1
${docker_image}                 ${docker_image_name}:${docker_image_tag}
# TODO test base dir should change when running from Jenkins
${test_base_dir}                /home/cloudadmin/kinkwan/smoke_test/cloudtaf-27967fe/testcases/pm-support/misc
${custom_metrics_yaml_name}     custom-metrics-test-dep.yaml
${custom_metrics_pod_name}      custommetrics

*** Keywords ***
Create Custom Metrics Docker Image
    [Arguments]    ${node}=sudo-default
    ${cmd}=        cd ${test_base_dir} | docker build --network=host --no-cache --force-rm --tag ${docker_image_name}:${docker_image_tag} .
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

Push Custom Metrics Image
    [Arguments]    ${node}=sudo-default
    ${cmd}=        docker push ${docker_image}
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

Delete Custom Metrics Image
    [Arguments]    ${node}=sudo-default
    ${cmd}=        docker rmi ${docker_image} ${docker_image}
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

Delete Custom Metrics Pod
    [Arguments]    ${node}=sudo-default
    ${cmd}=        kubectl delete pod ${custom_metrics_pod_name}
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

Apply deployment yaml
    [Arguments]    ${node}=sudo-default
    ${cmd}=        kubectl apply -f ${test_base_dir}/${custom_metrics_yaml_name}
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

    ${cmd}=        kubectl get po -n kube-system | grep ${custom_metrics_pod_name}
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}
    Should not be empty     ${output.stdout}

Check custom metrics
    [Arguments]    ${node}=sudo-default
    ${cmd}=        kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}


    ${cmd}=        kubectl get –raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/kube-system/pods/*/http_requests
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}

Custom Metrics Teardown
    Delete Custom Metrics Pod
    Delete Custom Metrics Image


Check kubectl api
    [Arguments]    ${node}=sudo-default
    ${cmd}=    Set Variable    kubectl api-versions | grep metrics
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}
    Should Contain   ${output}       custom.metrics.k8s.io/v1beta1
    Should Contain   ${output}       metrics.k8s.io/v1beta1

Check Core Metrics
    [Arguments]    ${node}=sudo-default
    ${cmd}=    Set Variable    kubectl top node
    ${output}=     Ssh.Execute Command    ${cmd}      ${node}
    Should Not Contain   ${output}       " 0m"
    Should Not Contain   ${output}       " 0Mi"


*** Test Cases ***

PM001
     ${output}=     Ssh.Execute Command    ls -la     sudo-default
     Log to console     ${output}
     ${output}=     Execute Command    ls -la
     Log to console     ${output}

#    Create Custom Metrics Docker Image
#    Push Custom Metrics Image
#    Apply deployment yaml
#    Check custom metric
#    [Teardown]   Custom Metrics Teardown

PM002
    Check kubectl api

PM003
    Check Core Metrics
