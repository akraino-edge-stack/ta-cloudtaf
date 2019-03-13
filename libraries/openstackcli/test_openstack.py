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
import os
import json
from collections import namedtuple
import pytest
from . openstackcli import (
    OpenStack,
    OpenStackCliError)


class MockResult(namedtuple('MockResult', ['status', 'stdout', 'stderr'])):
    def __str__(self):
        return ', '.join([
            '{n}: {v!r}'.format(n=n, v=v) for n, v in self._asdict().items()])


def get_output():
    return _get_content('service_show_neutron_expected_output.txt')


def _get_content(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


@pytest.mark.parametrize('return_value', [
    MockResult(status=0, stdout=get_output(), stderr=''),
    MockResult(status='0', stdout=get_output(), stderr='')])
def test_openstack_run(cliwrapper, return_value):
    cliwrapper.set_exec_func_and_return_value(
        cliwrapper.remotesession.execute_command_in_target,
        return_value=return_value)
    cliwrapper.set_expected_cmd_postfix(' -f json')

    ret = cliwrapper.run_with_verify(cliwrapper.cli.run, 'service show neutron')

    runner_out = return_value.stdout
    assert json.loads(runner_out) == ret


def test_run_ignore_output(cliwrapper):
    return_value = MockResult(status=0, stdout='', stderr='')
    cliwrapper.set_exec_func_and_return_value(
        cliwrapper.remotesession.execute_command_in_target,
        return_value=return_value)

    cliwrapper.run_with_verify(cliwrapper.cli.run_ignore_output, 'cmd')


def test_run_raw(cliwrapper):
    return_value = MockResult(status=0, stdout='output', stderr='')
    cliwrapper.set_exec_func_and_return_value(
        cliwrapper.remotesession.execute_command_in_target,
        return_value=return_value)

    assert cliwrapper.run_with_verify(cliwrapper.cli.run_raw,
                                      'cmd') == return_value.stdout


def test_openstack_run_nohup(cliwrapper):
    runner = cliwrapper.remotesession.get_remoterunner.return_value
    return_value = 'pid'
    cliwrapper.set_exec_func_and_return_value(
        runner.execute_nohup_background_in_target,
        return_value=return_value)

    assert cliwrapper.run_with_verify(cliwrapper.cli.run_nohup,
                                      'cmd') == return_value


@pytest.fixture
def openstack(mock_remotesession):
    n = OpenStack()
    n.initialize(mock_remotesession)
    return n


class RemoteException(Exception):
    pass


def raise_remoteexception():
    raise RemoteException('message')


def test_openstack_run_runner_raises(mock_remotesession,
                                     openstack):

    mock_remotesession.execute_command_in_target.side_effect = (
        lambda cmd, target: raise_remoteexception())

    with pytest.raises(OpenStackCliError) as excinfo:
        openstack.run('cmd')

    assert str(excinfo.value) == (
        "Remote command 'openstack --os-cloud default cmd -f json' "
        "in target 'default' failed: RemoteException: message")


@pytest.fixture(params=[
    MockResult(status=1, stdout='out', stderr=''),
    MockResult(status=0, stdout='out', stderr='err'),
    MockResult(status='zero', stdout='out', stderr='')])
def bad_mock_remotesession(request,
                           mock_remotesession):
    mock_remotesession.execute_command_in_target.return_value = (
        request.param)
    return mock_remotesession


def test_openstack_run_result_fail(bad_mock_remotesession,
                                   methodfmt):
    with pytest.raises(OpenStackCliError) as excinfo:
        methodfmt.method('cmd')

    execute = bad_mock_remotesession.execute_command_in_target
    assert str(excinfo.value) == (
        "Remote command 'openstack --os-cloud default cmd{fmt}' "
        "in target 'default' failed: {return_value}".format(
            fmt=methodfmt.fmt,
            return_value=execute.return_value))


def test_run_nohup_runner_raises(mock_remotesession,
                                 openstack):

    runner = mock_remotesession.get_remoterunner.return_value
    runner.execute_nohup_background_in_target.side_effect = (
        lambda cmd, target: raise_remoteexception())

    with pytest.raises(OpenStackCliError) as excinfo:
        openstack.run_nohup('cmd')

    assert str(excinfo.value) == (
        "Remote command 'openstack --os-cloud default cmd' "
        "in target 'default' failed: RemoteException: message")
