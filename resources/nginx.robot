
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
Library             crl.remotesession.remotesession.RemoteSession
...                 WITH NAME    RemoteSession
Resource            ssh.robot


*** Variables ***
${IMAGE_NAME} =  nginx
${VERSION} =  1.17


*** Keywords ***
Apply Yaml
    ${image_file} =  Set Variable  ${IMAGE_NAME}.${VERSION}
    RemoteSession.Copy File To Target  resources/${image_file}.yaml  /tmp
    ${result} =  RemoteSession.Execute Command In Target  kubectl apply -f /tmp/${image_file}.yaml
    Log  ${result}
    Wait Until Keyword Succeeds  6x  10s  Pod Running

Pod Running
    ${command} =  set variable  kubectl get pods --field-selector=status.phase==Running | grep ${IMAGE_NAME} | wc -l
    ${result} =  RemoteSession.Execute Command In Target    ${command}
    Should Be Equal As Numbers  ${result.stdout}  1

Delete Yaml
    ${image_file} =  Set Variable  ${IMAGE_NAME}.${VERSION}
    ${image_tag} =  Set Variable  ${IMAGE_NAME}:${VERSION}
    RemoteSession.Execute Command In Target  kubectl delete -f /tmp/${IMAGE_NAME}.${VERSION}.yaml
    RemoteSession.Execute Command In Target  rm /tmp/${image_tag}.yaml
    RemoteSession.Execute Command In Target  docker image rm ${image_tag}
    RemoteSession.Execute Command In Target  rm /tmp/${image_tag}.tar