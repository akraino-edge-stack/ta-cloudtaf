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

from openstackcli import (
    OpenStack,
    Runner)
from .hostcli import HostCli


class HostCliUser(object):  # pylint: disable=too-few-public-methods
    """Base class for users of the
        - :class:`OpenStack`
        - :class:`Runner`
        - `crl.remotesession.remotesession.RemoteSession`

    instances.

    Attributes:

       _hostcli: :class:`HostCli` instance

       _openstack: :class:`.OpenStack` instance

       _runner: :class:`.Runner` instance

       _remotesession: :class:`crl.remotesession.remotesession.RemoteSession`
                       instance.

    """
    def __init__(self):
        self._hostcli = HostCli()
        self._openstack = OpenStack()
        self._runner = Runner()
        self._remotesession = None
        self._envname = None

    def initialize(self, remotesession, envname=None):
        self._remotesession = remotesession
        self._envname = envname
        envkwargs = {} if envname is None else {'envname': envname}
        for runner in [self._hostcli, self._openstack, self._runner]:
            runner.initialize(remotesession, **envkwargs)

    def _get_env_target(self, target='default'):
        """Get ennvironment target for the *target*.
        """
        return '{target}{env_postfix}'.format(
            target=target,
            env_postfix=self._env_postfix)

    @property
    def _env_postfix(self):
        return '.{}'.format(self._envname) if self._envname else ''
