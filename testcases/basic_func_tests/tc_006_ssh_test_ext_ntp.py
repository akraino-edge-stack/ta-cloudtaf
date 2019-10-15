import sys
import os
import json
import re
import time
from datetime import datetime
from datetime import timedelta

from decorators_for_robot_functionalities import *
from robot.api import logger
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
import common_utils
from test_constants import *
from robot.libraries.BuiltIn import BuiltIn

ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')


def tc_006_ssh_test_ext_ntp():
    steps = ['step1_check_ntpd_service_and_ext_ntp_ip_on_crf_nodes']
    common_utils.keyword_runner(steps)


def step1_check_ntpd_service_and_ext_ntp_ip_on_crf_nodes():
    crf_nodes = stack_infos.get_crf_nodes()
    check_ntpd_status(crf_nodes)
    check_if_nokia_ntp_server_address_set_on_crf_node(crf_nodes)


@Robot_log
def check_ntpd_status(nodes):
    if not nodes:
        logger.info("Nodes dictionary is empty, nothing to check.")
        return
    command = 'systemctl status ntpd.service | grep --color=no "Active"'
    for node in nodes:
        logger.console("\nCheck ntpd status " + node + " " + nodes[node])
        stdout = ex.execute_unix_command_on_remote_as_user(command, nodes[node])
        if "running" not in stdout:
            raise Exception("ntpd.service is not running!")


@Robot_log
def get_ext_ntp_ips_from_node():
    return stack_infos.get_inventory()["all"]["vars"]["time"]["ntp_servers"]


@Robot_log
def filter_valid_ntp_servers(ntp_servers):
    valid_servers = []
    for server in ntp_servers:
        stdout, stderr = ex.execute_unix_command("ntpdate -q {}".format(server), fail_on_non_zero_rc=False)
        if "no server suitable for synchronization found" not in stdout:
            valid_servers.append(server)
    return valid_servers


@Robot_log
def is_ntp_server_set_on_node(server_ip, node):
    command = 'ntpq -pn | grep -w --color=no ' + server_ip
    stdout = ex.execute_unix_command_on_remote_as_user(command, node, {}, fail_on_non_zero_rc=False)
    return server_ip in str(stdout)


@Robot_log
def check_if_nokia_ntp_server_address_set_on_crf_node(nodes):
    ext_ntp_server_ips = get_ext_ntp_ips_from_node()
    valid_servers = filter_valid_ntp_servers(ext_ntp_server_ips)
    logger.info("The following ntp_servers will be tested:")
    logger.info(valid_servers)
    is_ip_set = True
    for node in nodes:
        for ntp_serv_ip in valid_servers:
            if not is_ntp_server_set_on_node(ntp_serv_ip, node):
                is_ip_set = False
    if not is_ip_set:
        raise Exception("Wrong or no NTP server address set!")
