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
import six
from . profiles import (
    MasterProfile,
    WorkerProfile,
    StorageProfile,
    BaseProfile,
    ManagementProfile)


class Host(object):
    def __init__(self, name, service_profiles, ippool):
        self.name = name
        self.service_profiles = service_profiles
        self.internal_ip = ippool.get_internal_ip()
        self.external_ip = ippool.get_external_ip()

    @property
    def host_dict(self):
        d = self._service_profiles_dict
        d.update({'network_domain': self.expected_network_domain})
        d.update(self._network_profiles_dict)
        return d

    @property
    def _service_profiles_dict(self):
        return {'service_profiles': [str(s()) for s in self.service_profiles]}

    @property
    def expected_network_domain(self):
        return '{name}-domain-name'.format(name=self.name)

    @property
    def _network_profiles_dict(self):
        return {'network_profiles': self._network_profiles}

    @property
    def _network_profiles(self):
        return ['network_nondpdk']

    @property
    def networking(self):
        return {'infra_internal': {'ip': self.internal_ip},
                'infra_external': {'ip': self.external_ip}}

    @property
    def network_profile_details(self):
        return {
            'network_nondpdk': {
                'provider_network_interfaces': {
                    'bond1': {
                        'type': 'ovs'}}},
            'network_empty': {}}

    @staticmethod
    def expected_is_dpdk():
        return False


class DpdkHost(Host):

    @property
    def _network_profiles(self):
        return ['network_dpdk']

    @property
    def network_profile_details(self):
        return {
            'network_dpdk': {
                'provider_network_interfaces': {
                    'bond1': {
                        'type': 'ovs-dpdk'}}}}

    @staticmethod
    def expected_is_dpdk():
        return True


@six.add_metaclass(abc.ABCMeta)
class HostGeneratorBase(object):
    """
    Abstract generator base for :class:`.Host` instances.

    Arguments:
       ippool: :class:`IPPool` instance
    """
    def __init__(self, ippool):
        self._ippool = ippool

    @property
    def _host_cls(self):
        return Host

    def gen(self, nmbr, service_profiles=None, start=1):
        service_profiles = service_profiles or self._default_profiles
        for i in range(start, start + nmbr):
            yield self._host_cls(
                name='{basename}-{i}'.format(basename=self._basename, i=i),
                service_profiles=service_profiles,
                ippool=self._ippool)

    @abc.abstractproperty
    def _basename(self):
        """Return basename of the host e.g. master"""

    @abc.abstractproperty
    def _default_profiles(self):
        """Return iterable of service profiles"""


class MasterGenerator(HostGeneratorBase):
    @property
    def _basename(self):
        return 'master'

    @property
    def _default_profiles(self):
        return [MasterProfile,
                WorkerProfile,
                StorageProfile,
                BaseProfile,
                ManagementProfile]


class WorkerGenerator(HostGeneratorBase):
    @property
    def _basename(self):
        return 'worker'

    @property
    def _default_profiles(self):
        return [WorkerProfile, BaseProfile]


class StorageGenerator(HostGeneratorBase):
    @property
    def _basename(self):
        return 'storage'

    @property
    def _default_profiles(self):
        return [StorageProfile]


class DpdkWorkerGenerator(WorkerGenerator):
    @property
    def _host_cls(self):
        return DpdkHost
