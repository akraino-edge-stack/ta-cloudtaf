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

import abc
import itertools
from collections import namedtuple
import pytest
import six
import mock
from crl.remotesession.remotesession import RemoteSession
from hostcli import HostCli
from .cluster import (
    MgmtTarget,
    Cluster,
    ClusterError)
from .testutils.profiles import (
    MasterProfile,
    WorkerProfile,
    StorageProfile,
    ManagementProfile,
    BaseProfile)
from .testutils.ippool import IPPool
from .testutils.host import (
    MasterGenerator,
    WorkerGenerator,
    DpdkWorkerGenerator)
from .metasingleton import MetaSingleton


class ClusterMocks(namedtuple('ClusterMocks', ['remotesession',
                                               'hostcli',
                                               'envcreator',
                                               'usermanager'])):
    pass


@six.add_metaclass(abc.ABCMeta)
class ClusterVerifierBase(object):

    _mgmt_target = MgmtTarget(host='host',
                              user='user',
                              password='password')

    _sudoshelldicts = [{'shellname': 'BashShell', 'cmd': 'sudo bash'}]

    def __init__(self, cluster_mocks):
        self._mocks = cluster_mocks
        self._ippool = IPPool()
        self._hosts = [h for h in self._hosts_gen()]
        self._cluster = None
        MetaSingleton.clear(Cluster)

    @property
    def cluster(self):
        if self._cluster is None:
            self._setup_cluster()
        return self._cluster

    def _setup_cluster(self):
        self._cluster = self._create_cluster()

    def verify_get_host(self):
        for h in self._hosts:
            actual_host = self.cluster.get_host(h.name)
            assert actual_host.shelldicts == self._expected_shelldicts(h), (
                'expected: {}, got: {}'.format(
                    self._expected_shelldicts(h),
                    actual_host.shelldicts))
            assert actual_host.network_domain == h.expected_network_domain, (
                'expected: {expected}, got: {actual}'.format(
                    expected=h.expected_network_domain,
                    actual=actual_host.network_domain))
            assert actual_host.is_dpdk == h.expected_is_dpdk()

    def verify_master_external_ip(self):
        for master in self._masters:
            actual_ip = self.cluster.get_host(master.name).external_ip
            assert actual_ip == master.external_ip, (
                'Expected external_ip : {expected}, actual: {actual}'.format(
                    expected=master.external_ip,
                    actual=actual_ip))

    @property
    def _masters(self):
        for h in self._hosts:
            if MasterProfile in h.service_profiles:
                yield h

    def verify_get_hosts_with_profiles(self):
        for profs, eh in self._expected_restricted_profs.items():
            expected_hosts = sorted(eh)
            hosts = self.cluster.get_hosts_with_profiles(*profs)
            assert hosts == expected_hosts, (
                'Expected hosts: {e}, got: {g}'.format(e=expected_hosts, g=hosts))

    def verify_hosts_containing(self):
        for p in self._profs_combinations():
            hosts = set(self.cluster.get_hosts_containing(*p))
            expected_hosts = set(self._get_expected_hosts_containing(set(p)))
            assert set(hosts) == expected_hosts, (
                'Expected hosts: {e}, got: {g}'.format(e=expected_hosts, g=hosts))

    def verify_initialize_remotesession(self):
        mock_remotesession = mock.create_autospec(RemoteSession).return_value
        self.cluster.initialize_remotesession(mock_remotesession)
        self._verify_initialize_mock_calls(mock_remotesession)

    def _verify_initialize_mock_calls(self, mock_remotesession):
        mock_remotesession.set_envcreator.assert_called_once_with(
            self._mocks.envcreator.return_value)
        self._verify_normal_and_sudo_mgmt(mock_remotesession)
        self._verify_remotescript_default(mock_remotesession)
        for h in self.cluster.get_hosts():
            self._verify_normal_and_sudo_host(h, mock_remotesession)

    def _verify_normal_and_sudo_mgmt(self, mock_remotesession):
        mgmtshelldicts = self.cluster.get_mgmt_shelldicts()
        self._should_be_in_set_runner(mock.call(mgmtshelldicts),
                                      mock_remotesession=mock_remotesession)
        sudodicts = mgmtshelldicts + self._sudoshelldicts
        self._should_be_in_set_runner(mock.call(shelldicts=sudodicts,
                                                name='sudo-default'),
                                      mock_remotesession=mock_remotesession)

    def _verify_remotescript_default(self, mock_remotesession):
        self._should_be_in_set_target(mock.call(host=self._mgmt_target.host,
                                                username=self._mgmt_target.user,
                                                password=self._mgmt_target.password,
                                                name='remotescript-default'),
                                      mock_remotesession=mock_remotesession)

    def _should_be_in_set_target(self, call, mock_remotesession):
        set_target_calls = self._get_set_target_calls(mock_remotesession)
        assert call in set_target_calls, (
            '{call} is not in {set_target_calls}'.format(
                call=call,
                set_target_calls=set_target_calls))

    @staticmethod
    def _get_set_target_calls(mock_remotesession):
        return mock_remotesession.set_target.mock_calls

    def _verify_normal_and_sudo_host(self, host, mock_remotesession):
        self._should_be_in_set_runner(mock.call(shelldicts=host.shelldicts,
                                                name=host.name),
                                      mock_remotesession=mock_remotesession)
        sudodicts = host.shelldicts + self._sudoshelldicts
        self._should_be_in_set_runner(mock.call(shelldicts=sudodicts,
                                                name='sudo-{}'.format(host.name)),
                                      mock_remotesession=mock_remotesession)

    def verify_create_remotesession(self):
        self._verify_initialize_mock_calls(self.cluster.create_remotesession())

    def _should_be_in_set_runner(self, call, mock_remotesession):
        set_runner_target_calls = self._get_set_runner_target_calls(mock_remotesession)
        assert call in set_runner_target_calls, (
            '{call} is not in {set_runner_target_calls}'.format(
                call=call,
                set_runner_target_calls=set_runner_target_calls))

    def verify_initialize_hostcli(self):
        mock_hostcli = mock.create_autospec(HostCli)
        self.cluster.initialize_hostcli(mock_hostcli)
        mock_hostcli.initialize.assert_called_once_with(
            self._mocks.remotesession.return_value)

    def verify_create_hostcli(self):
        assert self.cluster.create_hostcli() == self._mocks.hostcli.return_value
        assert self._mocks.hostcli.return_value.initialize.mock_calls == [
            mock.call(self._mocks.remotesession.return_value) for _ in range(2)]

    def verify_create_user_with_roles(self):
        roles = ['role1', 'role2']
        create_user = self._mocks.usermanager.return_value.create_user_with_roles
        assert self.cluster.create_user_with_roles(*roles) == create_user.return_value
        self._mocks.usermanager.assert_called_once_with(
            hostcli_factory=self._cluster.create_hostcli)
        create_user.assert_called_once_with(*roles)

    def verify_delete_users(self):
        self.cluster.delete_users()
        self._mocks.usermanager.assert_called_once_with(
            hostcli_factory=self._cluster.create_hostcli)
        self._mocks.usermanager.return_value.delete_users.assert_called_once_with()

    def verify_envcreator(self):
        self._setup_cluster()
        self._mocks.envcreator.assert_called_once_with(
            remotesession_factory=self.cluster.create_remotesession,
            usermanager=self._mocks.usermanager.return_value)

    @staticmethod
    def _get_set_runner_target_calls(mock_remotesession):
        return mock_remotesession.set_runner_target.mock_calls

    def verify_cluster_config_caching(self):
        self._create_cluster()
        cluster = Cluster()
        self._setup_cluster_and_verify(cluster)

    def verify_mgmt_shelldicts(self):
        assert self.cluster.get_mgmt_shelldicts() == [self._mgmt_target.asdict()]

    def verify_is_dpdk(self):
        assert self.cluster.is_dpdk() == self._expected_is_dpdk

    def verify_get_hosts_with_dpdk(self):
        assert self.cluster.get_hosts_with_dpdk() == sorted(self._expected_hosts_with_dpdk())

    def _expected_hosts_with_dpdk(self):
        for h in self._hosts:
            if h.expected_is_dpdk():
                yield h.name

    @property
    def _expected_is_dpdk(self):
        for h in self._hosts:
            if h.expected_is_dpdk():
                return True

        return False

    @abc.abstractmethod
    def _hosts_gen(self):
        """Return generator of :class:`.testutils.Host` instances."""

    def _create_cluster(self):
        c = Cluster()
        c.clear_cache()
        self._setup_cluster_and_verify(c)
        return c

    def _setup_cluster_and_verify(self, cluster):
        self._mocks.hostcli.return_value.run.return_value = self._configprops
        cluster.set_profiles(master=str(MasterProfile()), worker=str(WorkerProfile()))
        cluster.initialize(**self._mgmt_target.asdict())
        self._verify_after_initialize(cluster)

    def _verify_after_initialize(self, cluster):
        assert len(self._hosts) == len(cluster.get_hosts()), (
            len(self._hosts), len(cluster.get_hosts()))

        hostcli = self._mocks.hostcli.return_value
        hostcli.initialize.assert_called_once_with(
            self._mocks.remotesession.return_value)
        hostcli.run.assert_called_once_with('config-manager list properties')

    def _get_expected_hosts_containing(self, profs):
        hosts = set()
        for p, h in self._expected_profs.items():
            if profs.issubset(p):
                hosts = hosts.union(set(h))
        return hosts

    @property
    def _expected_restricted_profs(self):
        def profile_filter(prof):
            return prof in [MasterProfile, WorkerProfile, StorageProfile]

        return self._get_expected_profs_for_filter(profile_filter)

    @property
    def _expected_profs(self):
        return self._get_expected_profs_for_filter(lambda prof: True)

    def _get_expected_profs_for_filter(self, profile_filter):
        p = {}
        for host in self._hosts:
            key = frozenset([str(s()) for s in host.service_profiles if profile_filter(s)])
            if key not in p:
                p[key] = []
            p[key].append(host.name)
        return p

    @staticmethod
    def _profs_combinations():
        profs = [str(p()) for p in [MasterProfile,
                                    WorkerProfile,
                                    BaseProfile,
                                    ManagementProfile]]
        for r in range(1, len(profs) + 1):
            for p in itertools.combinations(profs, r):
                yield p

    def _expected_shelldicts(self, host):
        if MasterProfile in host.service_profiles:
            return [{'host': host.external_ip,
                     'user': self._mgmt_target.user,
                     'password': self._mgmt_target.password}]
        return [self._mgmt_target.asdict(),
                {'host': host.internal_ip,
                 'user': self._mgmt_target.user,
                 'password': self._mgmt_target.password}]

    @property
    def _configprops(self):
        return list(self._hosts_config_gen()) + [self._get_hosts_network_profiles()]

    def _hosts_config_gen(self):
        for h in self._hosts:
            yield {'property': '{host}.networking'.format(host=h.name),
                   'value': h.networking}

        yield {'property': 'cloud.hosts',
               'value': {h.name: h.host_dict for h in self._hosts}}

    def _get_hosts_network_profiles(self):
        return {'property': 'cloud.network_profiles',
                'value': self._get_network_profile_details()}

    def _get_network_profile_details(self):
        d = {}
        for h in self._hosts:
            d.update(h.network_profile_details)
        return d

    @property
    def _master_gen(self):
        return MasterGenerator(self._ippool).gen

    @property
    def _worker_gen(self):
        return WorkerGenerator(self._ippool).gen


class Type1Verifier(ClusterVerifierBase):
    # pylint: disable=not-callable
    def _hosts_gen(self):
        return itertools.chain(self._master_gen(3),
                               self._worker_gen(2))


class Type2Verifier(ClusterVerifierBase):

    def _hosts_gen(self):
        return itertools.chain(self._master_gen(3),
                               self._dpdk_worker_gen(2))

    @property
    def _dpdk_worker_gen(self):
        return DpdkWorkerGenerator(self._ippool).gen


class CorruptedVerifier(Type1Verifier):

    def _hosts_config_gen(self):
        yield {'property': 'not-relevant',
               'value': 'not-relevant'}

    def verify_corrupted_raises(self):
        with pytest.raises(ClusterError) as exinfo:
            self.cluster.get_host('somename')

        assert 'Property not found' in str(exinfo.value)
