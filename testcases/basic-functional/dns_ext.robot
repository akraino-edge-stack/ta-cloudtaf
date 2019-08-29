##############################################################################
# Copyright (c) 2019 AT&T Intellectual Property.                             #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License");            #
# you maynot use this file except in compliance with the License.            #
#                                                                            #
# You may obtain a copy of the License at                                    #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT  #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.           #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
##############################################################################

*** Settings ***
Library             Collections
Library             cluster.cluster.Cluster    WITH NAME    Cluster
Library             crl.remotesession.remotesession.RemoteSession
...                 WITH NAME    RemoteSession
Resource            ssh.robot
Resource            busybox.robot
Suite Setup         Run Keywords
...                 ssh.Setup Connections
...                 busybox.Create Manifest
Test Setup          ssh.Setup Connections
Suite Teardown      busybox.Delete Manifest


*** Variables ***
${DOMAIN}           rec.io


*** Test Cases ***
Verify Default Kubernetes Service DNS Name
    Testing Default Kubernetes Service DNS Name
Verify External DNS Service
    Testing External DNS Service


*** Keywords ***
Testing Default Kubernetes Service DNS Name
    ${pod_nslookup}=        set variable    kubectl exec -ti busybox -- nslookup kubernetes.default
    ${result}=    RemoteSession.Execute Command In Target    ${pod_nslookup}
    Should Be Equal As Numbers  ${result.status}    0


Testing External DNS Service
    ${pod_nslookup}=        set variable    kubectl exec -ti busybox -- nslookup google.com
    ${result}=    RemoteSession.Execute Command In Target    ${pod_nslookup}
    Should Be Equal As Numbers  ${result.status}    0