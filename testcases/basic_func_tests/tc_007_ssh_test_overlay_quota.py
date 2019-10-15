import sys
import os
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from test_constants import *
import common_utils

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')


def tc_007_ssh_test_overlay_quota():
    steps = ['step1_check_storage_driver_and_quota_setting',
             'step2_check_copy_files']
    common_utils.keyword_runner(steps)


def step1_check_storage_driver_and_quota_setting():
    logger.info("step1: check size of all container")
    command = "ps -eaf | grep --color=no dockerd | grep --color=no " \
              "'\-\-storage-driver overlay2 \-\-storage-opt overlay2.size='" + docker_size_quota
    nodes = stack_infos.get_all_nodes()
    for node in nodes:
        logger.info("\nchecking docker daemon settings on " + node + " : " + nodes[node])
        ex.execute_unix_command_on_remote_as_root(command, nodes[node])


def get_containerid_of_flannel_from_node(nodeIp):
    return ex.execute_unix_command_on_remote_as_root("docker ps | grep flanneld | cut -d ' ' -f1", nodeIp)


def allocate_file_on_node(nodeIp, size, file):
    command = "fallocate -l " + size + " /var/lib/docker/" + file
    return ex.execute_unix_command_on_remote_as_root(command, nodeIp)


def copy_file_to_container(nodeIp, containerId, file):
    command = "docker cp " + file + " " + containerId + ":/"
    return ex.execute_unix_command_on_remote_as_root(command, nodeIp, delay="120s")


def delete_files_from_container(nodeIp, containerId, listOfFiles):
    command = "docker exec -ti " + containerId + " rm -f /"
    for file in listOfFiles:
        ex.execute_unix_command_on_remote_as_root(command + file, nodeIp)


def delete_files_from_node(nodeIp, listOfFiles):
    command = "rm -f "
    for f in listOfFiles:
        ex.execute_unix_command_on_remote_as_root(command + '/var/lib/docker/' + f, nodeIp)


def test_copy_file(nodeIp, fileSize, fileName, containerId):
    allocate_file_on_node(nodeIp, fileSize, fileName)
    copy_file_to_container(nodeIp, containerId, "/var/lib/docker/" + fileName)


def step2_check_copy_files():
    crfNodes = stack_infos.get_crf_nodes()
    nodeIp = crfNodes.get("controller-1")
    if not nodeIp:
        raise Exception("controller-1 internal ip address is not available!")
    containerId = get_containerid_of_flannel_from_node(nodeIp)
    listOfFiles = ["tmp_file", "tiny_file"]
    file_size = str(int(docker_size_quota[:-1]) * 1024 - 5) + 'M'
    logger.info("step2: copy a smaller file than overlay quota to flannel.")
    test_copy_file(nodeIp, file_size, listOfFiles[0], containerId)
    logger.info("step2: copy 10 Mbytes file to flannel container. It should fail!")
    try:
        test_copy_file(nodeIp, "10M", listOfFiles[1], containerId)
    except Exception as e:
        if "no space left on device" not in str(e):
            raise e
        logger.info("file can't be copied to container as expected")
    delete_files_from_container(nodeIp, containerId, listOfFiles)
    delete_files_from_node(nodeIp, listOfFiles)
