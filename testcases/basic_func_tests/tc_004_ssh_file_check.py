import sys
import os
import common_utils

from robot.libraries.BuiltIn import BuiltIn
from test_constants import *
from robot.api import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')


def tc_004_ssh_file_check():
    steps = ['step1_openstack_file_check_on_crf_nodes']
    common_utils.keyword_runner(steps)


def step1_openstack_file_check_on_crf_nodes():
    check_file(stack_infos.get_crf_nodes(), '/opt/nokia/userconfig/', crf_node_openstack_file_types)


def check_file(nodes, folder, files):
    if not nodes:
        logger.info("Nodes dictionary is empty, nothing to check.")
        return
    for key in nodes:
        logger.console("\n" + key + " " + nodes[key])
        for f in files:
            full_file_path = folder + f
            command = 'ls ' + full_file_path + ' | wc -l'
            stdout = ex.execute_unix_command_on_remote_as_user(command, nodes[key])
            if stdout == "1":
                logger.console(full_file_path + " exists.")
            else:
                raise Exception(full_file_path + " not exists !")
