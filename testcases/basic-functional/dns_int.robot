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
Resource            nginx.robot
Suite Setup         Run Keywords
...                 ssh.Setup Connections
...                 nginx.Apply Yaml
Test Setup          ssh.Setup Connections
Suite Teardown      nginx.Delete Yaml


*** Variables ***
${DOMAIN}           rec.io


*** Test Cases ***
Verify Kubernetes Service DNS Name
    Testing Kubernetes Service DNS Name


*** Keywords ***
Testing Kubernetes Service DNS Name
    ${search}=     set variable    <h1>Welcome to nginx!</h1>
    ${curl_nginx}=        set variable    curl nginx.default.svc.${DOMAIN}
    ${result}=    RemoteSession.Execute Command In Target    ${curl_nginx}
    Should contain    ${result.stdout}    ${search}