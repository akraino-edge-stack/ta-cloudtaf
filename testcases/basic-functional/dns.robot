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
Test Setup          Run Keywords
...                 ssh.Setup Connections
...                 Create Busybox
Test Teardown       Run Keywords
...                 Delete Busybox

*** Variables ***
${DOMAIN}           rec.io


*** Keywords ***
Create Busybox
    ${command}=    set variable    kubectl apply -f https://k8s.io/examples/admin/dns/busybox.yaml
    ${create_deployment_out}=    RemoteSession.Execute Command In Target    ${command}
    log    ${create_deployment_out}


Delete Busybox
    ${cleanup}=    set variable    kubectl delete -f https://k8s.io/examples/admin/dns/busybox.yaml
    RemoteSession.Execute Command In Target    ${cleanup}


Testing Kubernetes Service DNS Name
    ${command}=    set variable    kubectl create deployment nginx --image=nginx; kubectl expose deployment nginx --port=80
    ${create_deployment_out}=    RemoteSession.Execute Command In Target    ${command}
    ${search}=     set variable    <h1>Welcome to nginx!</h1>
    ${curl_nginx}=        set variable    curl nginx.default.svc.${DOMAIN}
    ${result}=    RemoteSession.Execute Command In Target    ${curl_nginx}
    Should contain    ${result.stdout}    ${search}
    ${cleanup}=    set variable    kubectl delete service nginx; kubectl delete deployment nginx


Testing Default Kubernetes Service DNS Name
    ${pod_nslookup}=        set variable    kubectl exec -ti busybox -- nslookup kubernetes.default
    ${search}=     set variable    command terminated with exit code 1
    ${result}=    RemoteSession.Execute Command In Target    ${pod_nslookup}
    Should not contain    ${result.stdout}    ${search}


Testing External DNS Service
    ${pod_nslookup}=        set variable    kubectl exec -ti busybox -- nslookup google.com
    ${search}=     set variable    command terminated with exit code 1
    ${result}=    RemoteSession.Execute Command In Target    ${pod_nslookup}
    Should not contain    ${result.stdout}    ${search}


*** Test Cases ***
Verify Kubernetes Service DNS Name
    Testing Kubernetes Service DNS Name
Verify Default Kubernetes Service DNS Name
    Testing Default Kubernetes Service DNS Name
Verify External DNS Service
    Testing External DNS Service
