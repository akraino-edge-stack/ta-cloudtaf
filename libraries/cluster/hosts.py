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
from collections import namedtuple
import six


STORAGE = 'storage'


class Profiles(object):
    _master = None
    _worker = None

    @classmethod
    def set_profiles(cls, master, worker):
        cls._master = master
        cls._worker = worker

    @property
    def master(self):
        return self._master

    @property
    def worker(self):
        return self._worker

    @property
    def storage(self):
        return STORAGE

    @property
    def profiles_mask(self):
        return set([self.master, self.worker, self.storage])


class MgmtTarget(namedtuple('MgmtTarget', ['host', 'user', 'password'])):
    """Container for the cloudtaf2 management VIP target attributes.

    Arguments:
        host: IP address or FQDN of the host management VIP
        user: Username, e.g. cloudadmin for login
        password: Login password

    Example:

       Library    cluster.cluster.MgmtTarget
       ...    host=1.2.3.4
       ...    user=cloudadmin
       ...    password=good_password
    """

    def asdict(self):
        return self._asdict()


@six.add_metaclass(abc.ABCMeta)
class HostBase(object):
    """Container base for Host attributes.

    Attributes:
        name: name of the host
        service_profiles: list of service profiles like ['master', 'worker']
        shelldicts: list of dictionaries to RemoteSession.set_runner_target
    """
    def __init__(self, host_config):
        self._host_config = host_config

    @property
    def is_dpdk(self):
        """Return True if dpdk is used in provider network interfaces.
        In more detail, is True if and only if one of the network profiles has
        at least one interface with type *ovs-dpdk*.
        """
        return self._host_config.is_dpdk

    @property
    def name(self):
        return self._host_config.name

    @property
    def service_profiles(self):
        return self._host_config.service_profiles

    @property
    def network_domain(self):
        return self._host_config.network_domain

    @abc.abstractproperty
    def shelldicts(self):
        """Return *shelldicts* for :class:`crl.remotesession.remotesession`.
        """

    @property
    def _host_dict(self):
        return {'host': self._infra['ip'],
                'user': self._host_config.mgmt_target.user,
                'password': self._host_config.mgmt_target.password}

    @property
    def _infra(self):
        return self._host_config.networking['infra_{}'.format(self._infra_type)]

    @abc.abstractproperty
    def _infra_type(self):
        """Return any infra type e.g. 'internal', 'external' etc.
        """


class Master(HostBase):
    @property
    def shelldicts(self):
        return [self._host_dict]

    @property
    def _infra_type(self):
        return 'external'

    @property
    def external_ip(self):
        return self._infra['ip']


class NonMaster(HostBase):
    @property
    def shelldicts(self):
        return [self._host_config.mgmt_target.asdict(), self._host_dict]

    @property
    def _infra_type(self):
        return 'internal'


class HostConfig(namedtuple('HostConfig', ['name',
                                           'network_domain',
                                           'service_profiles',
                                           'networking',
                                           'mgmt_target',
                                           'is_dpdk'])):
    pass
