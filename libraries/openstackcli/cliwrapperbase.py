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


@six.add_metaclass(abc.ABCMeta)
class CliWrapperBase(object):
    """Test class base for CLI (openstackcli).
    """
    def __init__(self, clicls):
        self._cli = clicls()
        self._remotesession = None
        self._exec_func = None
        self._expected_cmd_postfix = ''

    @property
    def cli(self):
        return self._cli

    def set_remotesession(self, remotesession):
        """Set *RemoteSession* mock class instance.
        """
        self._remotesession = remotesession

    @property
    def remotesession(self):
        return self._remotesession

    def set_expected_cmd_postfix(self, expected_cmd_postfix):
        """Set expected cmd postfix for *RemoteSession* *exec_func* call.
        """
        self._expected_cmd_postfix = expected_cmd_postfix

    def set_exec_func_and_return_value(self, exec_func, return_value):
        """Set expected *RunnerSession* execution function and
        set mock return value for this call.
        """
        self._exec_func = exec_func
        self._exec_func.return_value = return_value

    def run_with_verify(self, run_method, cmd):
        """Run *run_method* of CLI with *cmd* and *_target_kwargs* kwargs. Then
        verify the *RemoteSession* *_exec_func* call.

        Return:
            *run_method* return value.
        """
        ret = run_method(cmd, **self._target_kwargs)
        self._exec_func.assert_called_once_with(
            self._get_expected_cmd(cmd + self._expected_cmd_postfix),
            target=self._expected_target)
        return ret

    @abc.abstractproperty
    def _expected_target(self):
        """Return expected target for RemoteSession call.
        """

    def _get_expected_cmd(self, cmd):
        return '{pre_cmd}{clistr}{expected_cmd_args}{cmd}'.format(
            pre_cmd=self._pre_cmd,
            clistr=self._clistr,
            expected_cmd_args=self._expected_cmd_args,
            cmd=cmd)

    @property
    def _clistr(self):
        n = self._cli.__class__.__name__
        return '' if n == 'Runner' else n.lower()

    @property
    def _pre_cmd(self):
        return ''

    @abc.abstractproperty
    def _target_kwargs(self):
        """Return target kwargs for *RemoteSession* method call.
        """

    @abc.abstractproperty
    def _expected_cmd_args(self):
        """Return args string after cli.
        """

    def initialize(self):
        """Initialize CLI with mock RemoteSession instance *remotesession*.
        """
        self._cli.initialize(self.remotesession)
