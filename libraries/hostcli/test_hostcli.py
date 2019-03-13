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
import pytest
import mock
from crl.remotesession.remotesession import RemoteSession
from crl.interactivesessions.remoterunner import RunResult
from .hostcli import HostCli


@pytest.fixture
def mock_remotesession():
    m = mock.create_autospec(RemoteSession)
    m.execute_command_in_target.return_value = RunResult(status=0,
                                                         stdout='"result"',
                                                         stderr='')
    return m


def test_hostcli(mock_remotesession):
    h = HostCli()
    h.initialize(mock_remotesession)
    assert h.run('cmd') == 'result'
    mock_remotesession.execute_command_in_target.assert_called_once_with(
        'hostcli --os-cloud default cmd -f json', target='default')
