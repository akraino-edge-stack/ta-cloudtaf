import sys
import os
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
import common_utils
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

ex = BuiltIn().get_library_instance('execute_command')
crf_nodes = BuiltIn().get_library_instance('stack_infos').get_crf_nodes()


def tc_005_ssh_dns_server_check():
    steps = ['step1_check_dns_server_replica_num_within_limits',
             'step2_dns_server_port_check',
             'step3_check_address_resolution']
    common_utils.keyword_runner(steps)


def step1_check_dns_server_replica_num_within_limits():
    command = "kubectl get daemonset kube-dns --namespace=kube-system | grep kube-dns | awk {'print $5'}"
    available_dns_replica_num = int(ex.execute_unix_command(command))
    if available_dns_replica_num < min_dns_replica:
        raise Exception(available_dns_replica_num + "DNS server is running! Minimum should be " + min_dns_replica + ".")
    if available_dns_replica_num > max_dns_replica:
        raise Exception(available_dns_replica_num + "DNS server is running! Maximum should be " + max_dns_replica + ".")


def step2_dns_server_port_check():
    nodes = get_nodes_containing_dns_servers()
    check_program_listening_on_given_port_protocol_on_remote(nodes, 'dnsmasq', 'tcp', dns_masq_port)
    check_program_listening_on_given_port_protocol_on_remote(nodes, 'kube-dns', 'tcp6', kube_dns_port)


def step3_check_address_resolution():
    ex.execute_unix_command("nslookup " + test_address1)
    ex.execute_unix_command("nslookup " + test_address2)
    logger.console("nslookup OK")


def get_nodes_containing_dns_servers():
    dns_nodes = {}
    logger.console("")
    for name, ip in crf_nodes.items():
        command = 'docker ps | grep dnsmasq | wc -l'
        stdout = int(ex.execute_unix_command_on_remote_as_user(command, ip))
        if stdout == 1:
            logger.console('DNS server running on ' + name + ':' + ip)
            dns_nodes[name] = ip
        if stdout > 1:
            raise Exception('Instead of one, ' + str(stdout) + ' DNS server running on node: ' + name + '!')
    return dns_nodes


def check_program_listening_on_given_port_protocol_on_remote(nodes, pname, proto, port):
    command = 'netstat -lopna | grep --color=no -P "' + proto + ' .*:' + port + '.*LISTEN.*"' + pname
    for name, ip in nodes.items():
        stdout = ex.execute_unix_command_on_remote_as_root(command, ip)
        logger.console(name + ':' + stdout)
