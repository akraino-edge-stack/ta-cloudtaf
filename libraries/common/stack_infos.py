import sys
import os
import json
import paramiko
from robot.libraries.BuiltIn import BuiltIn
from users import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class stack_infos:  # pylint: disable=invalid-name, old-style-class

    INVENTORY_PATH = "/opt/cmframework/scripts/inventory.sh"

    def __init__(self):
        self._floating_ip = BuiltIn().get_variable_value("${floating_ip}")

        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            client.connect(self._floating_ip,
                           username=cloudadmin['username'],
                           password=cloudadmin['password'])
            _, stdout, _ = client.exec_command(self.INVENTORY_PATH)
            self._inventory = json.loads(stdout.read())
        finally:
            client.close()

        self._crf_nodes = self.get_node_ip_based_on_caas_profile("caas_master")
        if not self._crf_nodes:
            raise Exception("crf_nodes dictionary is empty!")
        self._storage_nodes = self.get_node_ip_based_on_caas_profile("caas_storage")
        self._worker_nodes = self.get_node_ip_based_on_caas_profile("caas_worker")

    def get_floating_ip(self):
        return self._floating_ip

    def get_crf_nodes(self):
        return self._crf_nodes

    def get_storage_nodes(self):
        return self._storage_nodes

    def get_worker_nodes(self):
        return self._worker_nodes

    def get_all_nodes(self):
        all_nodes = self._crf_nodes.copy()
        all_nodes.update(self._storage_nodes)
        all_nodes.update(self._worker_nodes)
        return all_nodes

    def get_inventory(self):
        return self._inventory

    def get_node_ip_based_on_caas_profile(self, caas_profile):  # pylint: disable=invalid-name
        node_ip = {}
        if caas_profile in self._inventory:
            for node in self._inventory[caas_profile]:
                node_ip[node] = self._inventory["_meta"]["hostvars"][node]["networking"]["infra_internal"]["ip"]
        return node_ip

    def get_infra_int_if(self):
        interface = self._inventory["_meta"]["hostvars"]["controller-1"]["networking"]["infra_internal"]["interface"]
        return interface

    def get_infra_ext_if(self):
        iface = self._inventory["_meta"]["hostvars"]["controller-1"]["networking"]["infra_external"]["interface"]
        return iface

    def get_infra_storage_if(self):
        iface = self._inventory["_meta"]["hostvars"]["controller-1"]["networking"]["infra_storage_cluster"]["interface"]
        return iface

    def get_virtual_env(self):
        virtual_env = self._inventory["all"]["vars"]["virtual_env"]
        return virtual_env
