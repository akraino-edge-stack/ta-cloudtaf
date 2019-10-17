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
Test Setup          ssh.Setup Connections

*** Variables ***

*** Test Cases ***
Verify RBD Retain Policy
    RemoteSession.Copy File To Target  resources/pvc-cloudtaf.yaml  /tmp
    ${result} =  RemoteSession.Execute Command In Target  kubectl apply -f /tmp/pvc-cloudtaf.yaml
    Should Be Equal As Numbers  ${result.status}  0
    Sleep  2
    ${result} =  RemoteSession.Execute Command In Target  kubectl get pvc pvc-cloudtaf | awk 'NR==2{print $3}' 
    ${vc} =  Set Variable  ${result.stdout}
    ${result} =  RemoteSession.Execute Command In Target  kubectl get pv ${vc} -o json
    ${pv_json}    evaluate  json.loads('''${result.stdout}''')    json
    Log  ${pv_json}
    ${rbd_image} =  Set Variable  ${pv_json}[spec][rbd][image]
    ${rbd_pool} =  Set Variable  ${pv_json}[spec][rbd][pool]
    ${reclaimPolicy} =  Set Variable  ${pv_json}[spec][persistentVolumeReclaimPolicy]
    ${status} =  Set Variable  ${pv_json}[status][phase]
    
    Log  RBD Image: ${rbd_image}
    Log  RBD Pool: ${rbd_pool}
    Log  Reclaim Policy: ${reclaimPolicy}
    Log  Status: ${status}
    Should Be Equal  ${status}  Bound

    RemoteSession.Execute Command In Target  kubectl delete -f /tmp/pvc-cloudtaf.yaml
    RemoteSession.Execute Command In Target  rm /tmp/pvc-cloudtaf.yaml

    ${result} =  RemoteSession.Execute Command In Target  sudo rbd list -p ${rbd_pool} | grep ${rbd_image} | wc -l
    Run Key Word If  '${reclaimPolicy}'=='Retain'   Should Be Equal  ${result.stdout}  1
    Run Key Word If  '${reclaimPolicy}'=='Delete'   Should Be Equal  ${result.stdout}  0


*** Keywords ***


