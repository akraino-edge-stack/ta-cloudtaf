# Copyright 2019 Nokia
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

import logging
import six
from crl.remotesession.remotesession import RemoteSession
from crl.interactivesessions.shells.bashshell import BashShell
from hostcli import HostCli
from .envcreator import EnvCreator
from .usermanager import UserManager
from .metasingleton import MetaSingleton
from .hosts import (
    MgmtTarget,
    Master,
    NonMaster,
    Profiles,
    HostConfig)


LOGGER = logging.getLogger(__name__)


class ClusterError(Exception):
    pass


@six.add_metaclass(MetaSingleton)
class Cluster(object):
    """Singleton container for NCIR cluster hosts, their service profiles and
    access details.
    """
    def __init__(self):
        self._mgmt_target = None
        self._hosts = None
        self._configprops_cache = None
        self._usermanager = UserManager(hostcli_factory=self.create_hostcli)
        self._envcreator = EnvCreator(remotesession_factory=self.create_remotesession,
                                      usermanager=self._usermanager)

    def clear_cache(self):
        """Clears configprops cache."""
        self._configprops_cache = None

    def get_hosts(self):
        """Return Host containers of cluster.
        """
        return [h for _, h in self._hosts.items()]

    def initialize(self, host, user, password):
        """Initialize Cluster with management VIP

        Arguments:
            host:  Management VIP IP address
            user: Login username
            password: password for the user
        """
        self._mgmt_target = MgmtTarget(host=host, user=user, password=password)
        self._hosts = {hc.name: self._create_host(hc) for hc in self._host_configs()}

    @staticmethod
    def set_profiles(master, worker):
        """Set *service_profile' names of *master* and *worker* nodes
        """
        Profiles.set_profiles(master=master, worker=worker)

    def get_mgmt_shelldicts(self):
        """Return management VIP shelldicts for RemoteRunner.
        """
        return [self._mgmt_target.asdict()]

    def get_host(self, hostname):
        """Get Host container for hostname."""
        return self._hosts[hostname]

    def get_hosts_with_profiles(self, *service_profiles):
        """Get host names matching exactly *service_profiles*.
        """
        return sorted(list(self._get_hosts_with_profs_gen(set(service_profiles))))

    def get_hosts_containing(self, *service_profiles):
        """Get host names containing all  *service_profiles*.
        """
        return sorted(list(self._get_hosts_containing_gen(set(service_profiles))))

    def create_remotesession(self):
        """Create initialized *RemoteSession* instance.
        """
        r = RemoteSession()
        self.initialize_remotesession(r)
        return r

    def initialize_remotesession(self, remotesession):
        """Initialize :class:`crl.remotesession.remotesession.RemoteSession` instance
        with *shelldicts* and *name* of the hosts and sudo-<name> via *set_runner_target*.
        Initialize *default* target with *get_mgmt_shelldicts* return value.
        The sudo-<name> targets are terminals in target after executed roughly *sudo bash*.
        """
        self._set_mgmt_targets(remotesession)
        for host in self.get_hosts():
            remotesession.set_runner_target(shelldicts=host.shelldicts,
                                            name=host.name)
            remotesession.set_runner_target(
                shelldicts=self._get_sudoshelldicts(host.shelldicts),
                name='sudo-{}'.format(host.name))

        remotesession.set_envcreator(self._envcreator)

    def _set_mgmt_targets(self, remotesession):
        remotesession.set_runner_target(self.get_mgmt_shelldicts())
        remotesession.set_runner_target(
            shelldicts=self._get_sudoshelldicts(self.get_mgmt_shelldicts()),
            name='sudo-default')
        remotesession.set_target(host=self._mgmt_target.host,
                                 username=self._mgmt_target.user,
                                 password=self._mgmt_target.password,
                                 name='remotescript-default')

    @staticmethod
    def _get_sudoshelldicts(shelldicts):
        return shelldicts + [{'shellname': BashShell.__name__,
                              'cmd': 'sudo bash'}]

    def create_hostcli(self):
        """Create initialized *HostCli* instance.
        """
        n = HostCli()
        self.initialize_hostcli(n)
        return n

    def initialize_hostcli(self, hostcli):
        """Initialize :class:`crl.hostcli.HostCli` instance
        (or :class:`crl.hostcli.OpenStack`) with
        :class:`crl.remotesession.remotesession.RemoteSession` instance
        initialized with :meth:`.initialize_remotesession`.
        """
        hostcli.initialize(self.create_remotesession())

    def create_user_with_roles(self, *roles):
        """Create according to roles list.

        Special roles:

            all_roles: all roles in the system
            no_roles: empty role list

        Return:
            UserRecord of created user
        """
        return self._usermanager.create_user_with_roles(*roles)

    def delete_users(self):
        """Delete all users created by *Cluster*.
        """
        self._usermanager.delete_users()

    def is_dpdk(self):
        """Return *True* if *dpdk* is used in provider network interfaces.
        More detail, *True* if and only if there is at least one host with
        network profile providing *ovs-dpdk* type interface.
        """
        for _, h in self._hosts.items():
            if h.is_dpdk:
                return True
        return False

    def get_hosts_with_dpdk(self):
        """Returns list of hosts where *dpdk* is in use.
           In more detail, return sorted list of host names in which there is
           at least one network profile containing *dpdk* type interface.
        """
        return sorted([h.name for _, h in self._hosts.items() if h.is_dpdk])

    def _get_hosts_with_profs_gen(self, service_profiles):
        def filt(host):
            mask = Profiles().profiles_mask
            return not (service_profiles ^ set(host.service_profiles)) & mask

        return self._filtered_hostnames(filt)

    def _get_hosts_containing_gen(self, service_profiles):
        def filt(host):
            return service_profiles.issubset(set(host.service_profiles))

        return self._filtered_hostnames(filt)

    def _filtered_hostnames(self, filt):
        for h in self.get_hosts():
            if filt(h):
                yield h.name

    @staticmethod
    def _create_host(host_config):
        LOGGER.debug('host_config: %s', host_config)
        master = Profiles().master
        return (Master(host_config)
                if master in host_config.service_profiles else
                NonMaster(host_config))

    def _host_configs(self):
        LOGGER.debug('cloud_hosts: %s', self._cloud_hosts)
        for hostname, v in self._cloud_hosts.items():
            yield HostConfig(name=hostname,
                             network_domain=v['network_domain'],
                             service_profiles=v['service_profiles'],
                             networking=self._get_networking(hostname),
                             mgmt_target=self._mgmt_target,
                             is_dpdk=self._is_host_dpdk(v))

    def _is_host_dpdk(self, host_prop):
        network_profiles = set(host_prop['network_profiles'])
        return bool(network_profiles.intersection(set(self._dpdk_profiles())))

    def _dpdk_profiles(self):
        profiles = self._get_value_for_prop('cloud.network_profiles')
        for prof_n, prof_v in profiles.items():
            ifaces = prof_v.get('provider_network_interfaces', {})
            for _, iface_v in ifaces.items():
                if iface_v['type'] == 'ovs-dpdk':
                    yield prof_n

    @property
    def _cloud_hosts(self):
        return self._get_value_for_prop('cloud.hosts')

    def _get_networking(self, hostname):
        return self._get_value_for_prop('{}.networking'.format(hostname))

    def _get_value_for_prop(self, prop):
        for pv in self._configprops:
            if pv['property'] == prop:
                return pv['value']
        raise ClusterError('Property not found: {}'.format(prop))

    @property
    def _configprops(self):
        if self._configprops_cache is None:
            self._setup_configprops_cache()
        return self._configprops_cache

    def _setup_configprops_cache(self):
        s = RemoteSession()
        s.set_runner_target(self.get_mgmt_shelldicts())
        n = HostCli()
        n.initialize(s)
        self._configprops_cache = n.run('config-manager list properties')
