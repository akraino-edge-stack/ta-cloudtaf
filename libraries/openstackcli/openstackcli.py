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

"""Test library for running *openstack* in remote system.
"""
import abc
import json
from collections import namedtuple
from contextlib import contextmanager
import six


class OpenStackCliError(Exception):
    """Exception raised in case CLI in the remote system fails.
    """
    pass


class _FailedMessage(namedtuple('FailedMessage', ['cmd', 'target'])):
    def __str__(self):
        return "Remote command '{cmd}' in target '{target}' failed".format(
            cmd=self.cmd,
            target=self.target)


@six.add_metaclass(abc.ABCMeta)
class _TargetBase(object):

    @abc.abstractproperty
    def target(self):
        """Return *RemoteSession* target where command is to be executed
        """

    @abc.abstractproperty
    def cmd_template(self):
        """Return cmd template with field *cli*, *cmd* and *fmt*.
        """


class _DefaultTarget(_TargetBase):
    def __init__(self):
        self._raw_target = None
        self._target = None
        self._cloud = 'default'

    def set_target(self, target):
        self._raw_target = target
        self._setup()

    def _setup(self):
        self._target = self._raw_target
        if self._partslen == 2 or self._partslen == 3:
            self._update_target_and_cloud()

    def _update_target_and_cloud(self):
        if self._oper == 'os-cloud':
            self._target = self._parts[0] if self._partslen == 3 else 'default'
            self._cloud = self._parts[-1]
        elif self._partslen == 2:
            self._cloud = None

    @property
    def _oper(self):
        return self._parts[self._partslen - 2]

    @property
    def _parts(self):
        return self._raw_target.split('.')

    @property
    def _partslen(self):
        return len(self._parts)

    @property
    def target(self):
        return self._target

    @property
    def cmd_template(self):
        return ('{cli} {cmd}{fmt}'
                if self._cloud is None else
                '{{cli}} --os-cloud {cloud} {{cmd}}{{fmt}}'.format(cloud=self._cloud))


class _CliRunnerInTarget(object):
    def __init__(self, run, target):
        self._run = run
        self._target = target
        self._cli = None

    def set_cli(self, cli):
        self._cli = cli

    def run_with_json(self, cmd):
        return self._run_with_verification(cmd, fmt=' -f json')

    def run(self, cmd):
        return self._run_with_verification(cmd)

    def _run_with_verification(self, cmd, fmt=''):
        cmd = self._get_formatted_cmd(cmd, fmt)
        result = self._run(cmd, self._target.target)
        self._verify_result(result, _FailedMessage(cmd, self._target.target))
        return result

    def run_without_verification(self, cmd, fmt=''):
        return self._run(self._get_formatted_cmd(cmd, fmt), self._target.target)

    def _get_formatted_cmd(self, cmd, fmt):
        return self._target.cmd_template.format(cli=self._cli,
                                                cmd=cmd,
                                                fmt=fmt)

    def _verify_result(self, result, failedmessage):
        status = self._get_integer_status(result, failedmessage)
        if status or result.stderr:
            self._raise_openstackerror(failedmessage, result)
        return result

    def _get_integer_status(self, result, failedmessage):
        try:
            return int(result.status)
        except ValueError:
            self._raise_openstackerror(failedmessage, result)

    @staticmethod
    def _raise_openstackerror(failedmessage, result):
        raise OpenStackCliError(
            '{failedmessage}: status: {status!r}, '
            'stdout: {stdout!r}, '
            'stderr: {stderr!r}'.format(failedmessage=failedmessage,
                                        status=result.status,
                                        stdout=result.stdout,
                                        stderr=result.stderr))


class OpenStack(object):
    """Remote *openstack* runner.
    The runner executes commands in *crl.remotesession* target but the target
    *os-cloud.cloudconfigname* is interpreted to *--os-cloud cloudconfigname*
    argument and executed in the *default* target. Respectively, the target
    *controller-1.os-cloud.cloudconfigname* is executed in *controller-1*
    target with *--os-cloud cloudconfigname*.

    If the *target* is of form *target.envname*, then *--os-cloud* is not given
    as *crl.remotesession* environment handling should then take care of
    setting the correct environment for the *envname* in *target*.
    """

    def __init__(self):
        self._remotesession = None
        self._envname = None
        self._openrc_tuples = {}

    def initialize(self, remotesession, envname=None):
        """Initialize the library.

        Args:
            remotesession: `crl.remotesession.remotesession.RemoteSession`_
                           instance

            envname: Environment name appended to the target in form target.envname.
                     See Robot example 2 for details of the usage.

        **Note:**

           Targets are interpreted in the following manner:

           ============================== ==================== ====================
           Target                         RemoteSession target os-cloud config name
           ============================== ==================== ====================
           os-cloud.confname              default              confname
           controller-1.os-cloud.confname controller-1         confname
           target.envname                 target.envname       None
           ============================== ==================== ====================

        **Robot Examples**

            In the following example is assumed that
            `crl.remotesession.remotesession.RemoteSession`_ is imported in
            Library settings *WITH NAME* RemoteSession.


        *Example 1*

            ====================   =====================  =============
            ${remotesession}=      Get Library Instance   RemoteSession
            OpenStack.Initialize   ${remotesession}
            ====================   =====================  =============

        *Example 2*

            If in the test setup initialization is done with given *myenv* environment

            ====================   =====================  =============
            ${remotesession}=      Get Library Instance   RemoteSession
            OpenStack.Initialize   ${remotesession}       envname=myenv
            ====================   =====================  =============

            Then

            =============  ==========  =============
            OpenStack.Run  quota show  target=target
            =============  ==========  =============

            runs *openstack quota show* in the target *target.myenv*.

        .. _crl.remotesession.remotesession.RemoteSession:
           https://crl-remotesession.readthedocs.io/en/latest
           /crl.remotesession.remotesession.RemoteSession.html
        """
        self._remotesession = remotesession
        self._envname = envname

    def run(self, cmd, target='default'):
        """ Run *openstack* in the remote target with *json* format.

        Args:
            cmd: openstack command to be executed in target.

            target: `crl.remotesession.remotesession.RemoteSession`_ target.

        Returns:
            Decoded *json* formatted command output. For example in case
            openstack output (
            for command *openstack.run('quota show')* is in remote::

                # openstack --os-cloud default quota show -f json
                {
                 "secgroups": 10,
                 "health_monitors": null,
                 "l7_policies": null,
                 ...
                }

            then the return value of *run* is:

            .. code-block:: python

                {
                  "secgroups": 10,
                  "health_monitors": None,
                  "17_policies": None,
                  ...
                }

        **Robot Example:**

            ================ ===================== ===========
            ${quota}=        OpenStack.Run         quota show
            Should Be Equal  ${quota['secgroups']} 10
            ================ ===================== ===========

        Raises:
            OpenStackCliError: if remote *openstack* fails.

        .. _crl.remotesession.remotesession.RemoteSession:
           https://crl-remotesession.readthedocs.io/en/latest
           /crl.remotesession.remotesession.RemoteSession.html
        """
        result = self._create_runner(target).run_with_json(cmd)
        with self._error_handling(cmd, target):
            return json.loads(result.stdout)

    def run_ignore_output(self, cmd, target='default'):
        """ Run *openstack* in the remote target and ignore the output.

        Args:
            cmd: openstack command to be executed in target.

            target: `crl.remotesession.remotesession.RemoteSession`_ target.

        Returns:
            Nothing

        Raises:
            OpenStackCliError: if remote *openstack* fails.

        .. _crl.remotesession.remotesession.RemoteSession:
           https://crl-remotesession.readthedocs.io/en/latest
           /crl.remotesession.remotesession.RemoteSession.html
        """
        self._create_runner(target).run(cmd)

    def run_raw(self, cmd, target='default'):
        """ Run *openstack* in the remote target and return raw output without
        formatting.

        Args:
            cmd: openstack command to be executed in target.

            target: `crl.remotesession.remotesession.RemoteSession`_ target.

        Returns:
            Nothing

        Raises:
            OpenStackCliError: if remote *openstack* fails.

        .. _crl.remotesession.remotesession.RemoteSession:
           https://crl-remotesession.readthedocs.io/en/latest
           /crl.remotesession.remotesession.RemoteSession.html
        """
        return self._create_runner(target).run(cmd).stdout

    def run_nohup(self, cmd, target='default'):
        """ Run *openstack* in the remote target nohup mode in background and
        return PID of the started process.

        Note:
            This keyword is available only for targets initialized by
            *Set Runner Target* keyword of *RemoteSession*. The version of
            crl.interactivesessions must be at least as new as
            crl.interactivesessions==1.0b4.

        Args:
            cmd: openstack command to be executed in target.

            target: `crl.remotesession.remotesession.RemoteSession`_ target.

        Returns:
            PID of the process running *cmd* in the target.

        Raises:
            OpenStackCliError: if remote *openstack* fails.

        .. _crl.remotesession.remotesession.RemoteSession:
           https://crl-remotesession.readthedocs.io/en/latest
           /crl.remotesession.remotesession.RemoteSession.html
        """
        return self._create_runner(
            target, run=self._nohup_run).run_without_verification(cmd)

    def _create_runner(self, target, run=None):
        run = self._run if run is None else run
        r = _CliRunnerInTarget(run, self._get_target(target))
        r.set_cli(self._get_cli())
        return r

    def _get_target(self, target):
        return self._create_default_target(target)

    def _create_default_target(self, target):
        t = _DefaultTarget()
        t.set_target(self._get_envtarget(target))
        return t

    def _get_envtarget(self, target):
        return target if self._envname is None else '{target}.{envname}'.format(
            target=target,
            envname=self._envname)

    @classmethod
    def _get_cli(cls):
        return cls.__name__.lower()

    def _run(self, cmd, target):
        with self._error_handling(cmd, target):
            return self._remotesession.execute_command_in_target(
                cmd, target=target)

    def _nohup_run(self, cmd, target):
        runner = self._remotesession.get_remoterunner()
        with self._error_handling(cmd, target):
            return runner.execute_nohup_background_in_target(cmd,
                                                             target=target)

    @staticmethod
    @contextmanager
    def _error_handling(cmd, target):
        try:
            yield None
        except Exception as e:  # pylint: disable=broad-except
            raise OpenStackCliError(
                "{failed_msg}: {ecls}: {e}".format(
                    failed_msg=_FailedMessage(cmd, target),
                    ecls=e.__class__.__name__,
                    e=e))


class Runner(OpenStack):
    """The same as OpenStack_ but the remote command is executed withou prefix.

    **Note:**

    The Robot documentation of keywords is for *openstack* only.

    .. _OpenStack:  crl.openstack.OpenStack.html
    """

    @staticmethod
    def _get_cli():
        return ''
