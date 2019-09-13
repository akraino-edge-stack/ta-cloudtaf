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
...                 Create PersistentVolumeClaim
...                 Create pod with RBD
Test Teardown       Run Keywords
...                 Delete pod
...                 Delete PVC

*** Variables ***

${test_base_dir}                /cloudtaf/testcases/ceph_filecheck
${pvc_yaml_name}                pvc.yaml
${pod_with_rbd_yaml_name}       pod-with-rbd.yaml

*** Keywords ***

Create PersistentVolumeClaim
    ${search}=     set variable    persistentvolumeclaim/myclaim created
    ${command}=    set variable    kubectl create -f ${test_base_dir}/${pvc_yaml_name}
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Verify the PVC was created and bound to the expected PV
    ${search}=     set variable    Bound
    ${command}=    set variable    kubectl get pvc myclaim
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Create pod with RBD
    ${search}=     set variable    pod/mypod created
    ${command}=    set variable    kubectl create -f ${test_base_dir}/${pod_with_rbd_yaml_name}
    sleep          30s
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Check pod is created with Attached Volume
    ${search}=     set variable    SuccessfulAttachVolume
    ${command}=    set variable    kubectl describe pod mypod
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Verify the container mounts Ceph RBD Volume

    ${search}=     set variable    /mnt/rbd
    ${command}=    set variable    kubectl exec mypod -- df -h | grep rbd
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Delete pod
    ${search}=     set variable    pod "mypod" deleted
    ${command}=    set variable    kubectl delete pod mypod
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}
    
Delete PVC
   ${search}=     set variable     persistentvolumeclaim "myclaim" deleted
    ${command}=    set variable    kubectl delete pvc myclaim
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

*** Test Cases ***

Verify Ceph RBD File Check
    Verify the PVC was created and bound to the expected PV
    Check pod is created with Attached Volume
    Verify the container mounts Ceph RBD Volume
