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

# pylint: disable=redefined-outer-name
from collections import namedtuple
import mock
import pytest
from openstackcli import (
    OpenStack,
    Runner)
from . import hostcliuser
from .hostcli import HostCli
from .hostcliuser import HostCliUser


@pytest.fixture
def mock_hostcli():
    with mock.patch.object(hostcliuser, 'HostCli',
                           mock.create_autospec(HostCli)) as p:
        yield p


@pytest.fixture
def mock_openstack():
    with mock.patch.object(hostcliuser,
                           'OpenStack',
                           mock.create_autospec(OpenStack)) as p:
        yield p


@pytest.fixture
def mock_runner():
    with mock.patch.object(hostcliuser,
                           'Runner',
                           mock.create_autospec(Runner)) as p:
        yield p


@pytest.fixture(params=[{},
                        {'envname': 'envname'},
                        {'envname': 'otherenv'}])
def envkwargs(request):
    return request.param


@pytest.fixture
def examplehostcliuser(mock_remotesession,
                       mock_runners,
                       envkwargs):
    e = ExampleHostCliUser(mock_runners,
                           mock_remotesession=mock_remotesession,
                           envkwargs=envkwargs)
    e.initialize(mock_remotesession, **envkwargs)
    for runner in mock_runners:
        initialize = runner.return_value.initialize
        initialize.assert_called_once_with(mock_remotesession, **envkwargs)
    return e


@pytest.fixture
def mock_runners(mock_hostcli, mock_openstack, mock_runner):
    return MockRunners(hostcli=mock_hostcli,
                       openstack=mock_openstack,
                       runner=mock_runner)


class ExampleHostCliUser(HostCliUser):

    def __init__(self, mock_runners, mock_remotesession, envkwargs):
        super(ExampleHostCliUser, self).__init__()
        self._mock_runners = mock_runners
        self._mock_remotesession = mock_remotesession
        self._envkwargs = envkwargs

    @property
    def cmd(self):
        return 'cmd'

    def verify_runs(self):
        target = 'target'
        for rm in self._runnermocks:
            mock_run = rm.mock.return_value.run
            assert rm.runner.run(self.cmd, target=target) == mock_run.return_value
            mock_run.assert_called_once_with(self.cmd, target=target)

            execute = self._mock_remotesession.execute_command_in_target
            assert self._remotesession.execute_command_in_target(
                self.cmd, target=target) == execute.return_value

    @property
    def _runnermocks(self):
        yield RunnerMock(runner=self._hostcli, mock=self._mock_runners.hostcli)
        yield RunnerMock(runner=self._openstack, mock=self._mock_runners.openstack)
        yield RunnerMock(runner=self._runner, mock=self._mock_runners.runner)

    def verify_get_env_target(self):
        postfix = ('.{}'.format(self._envkwargs['envname'])
                   if self._envkwargs else
                   '')
        assert self._get_env_target() == 'default{}'.format(postfix)
        assert self._get_env_target('target') == 'target{}'.format(postfix)


class RunnerMock(namedtuple('RunMock', ['runner', 'mock'])):
    pass


class MockRunners(namedtuple('MockRunners', ['hostcli', 'openstack', 'runner'])):
    pass


def test_hostcliuser_runners(examplehostcliuser):
    examplehostcliuser.verify_runs()


def test_get_env_target(examplehostcliuser):
    examplehostcliuser.verify_get_env_target()
