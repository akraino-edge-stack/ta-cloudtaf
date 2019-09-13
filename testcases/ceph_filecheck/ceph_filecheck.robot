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

Creating PersistentVolumeClaim
    ${search}=     set variable    persistentvolumeclaim/myclaim created
    ${command}=    set variable    kubectl create -f pvc.yaml
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Verify the PVC was created and bound to the expected PV
    ${search}=     set variable    Bound
    ${command}=    set variable    kubectl get pvc
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Creating pod with RBD
    ${search}=     set variable    pod/mypod created
    ${command}=    set variable    kubectl create -f pod-with-rbd.yaml
    sleep          30s 
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Checking created pod with Attached Volume 
    ${search}=     set variable    SuccessfulAttachVolume
    ${command}=    set variable    kubectl describe pod mypod
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Verifying the container mounts Ceph RBD Volume 

    ${search}=     set variable    /mnt/rbd
    ${command}=    set variable    kubectl exec mypod -- df -h | grep rbd
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

Delete the pod
    ${search}=     set variable    pod "mypod" deleted
    ${command}=    set variable    kubectl delete pod mypod 
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}
Delete the PVC
   ${search}=     set variable     persistentvolumeclaim "myclaim" deleted
    ${command}=    set variable    kubectl delete pvc myclaim
    ${out}=    ssh.Execute Command    ${command}    controller-1
    log    ${out}
    Should contain    ${out}    ${search}

*** Test Cases ***
Test to create pod with RBD
    Creating PersistentVolumeClaim
Test to Verify the PVC was created and bound to the expected PV
    Verify the PVC was created and bound to the expected PV
Test to Creating pod with RBD
    Creating pod with RBD
Test to Checking created pod with Attached Volume
    Checking created pod with Attached Volume
Test to Verifying the container mounts Ceph RBD Volume
    Verifying the container mounts Ceph RBD Volume
Test to Delete the pod
    Delete the pod
Delete the PVC
    Delete the PVC
