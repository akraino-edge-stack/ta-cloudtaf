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

import os
import mock
from crl.remotesession.remotesession import RemoteSession
from crl.interactivesessions.remoterunner import RunResult
from .usermanager import (
    UserManager,
    UserRecord)
from .envcreator import EnvCreator


UPDATE_ENV_DICT = {
    'OS_ENDPOINT_TYPE': 'internalURL',
    'OS_USERNAME': 'admin',
    'OS_PASSWORD': 'password',
    'OS_TENANT_NAME': 'admin',
    'OS_PROJECT_NAME': 'admin',
    'OS_AUTH_URL': '192.168.1.2:5000/v3'}

UM_ADMIN_ENV_DICT = UPDATE_ENV_DICT.copy()
UM_ADMIN_ENV_DICT.update({'OS_USERNAME': 'um_admin_username',
                          'OS_PASSWORD': 'um_admin_password',
                          'OS_TENANT_NAME': 'infrastructure',
                          'OS_PROJECT_NAME': 'infrastructure'})

ROLES = ['role1', 'role2']

USERRECORD = UserRecord(uuid='uuid',
                        username='username',
                        password='password',
                        roles=ROLES)

TARGET = 'target'


THISDIR = os.path.dirname(__file__)
USER_CONFIG_PATH = os.path.join(THISDIR, 'testutils', 'user_config.yaml')


class EnvCreatorVerifier(object):
    def __init__(self):
        self._mock_remotesession_factory = mock.create_autospec(RemoteSession)
        self._mock_usermanager = mock.create_autospec(UserManager)
        self._envcreator = EnvCreator(
            remotesession_factory=self._mock_remotesession_factory,
            usermanager=self._mock_usermanager)
        self._setup_mocks()

    @property
    def _envname(self):
        return ', '.join(ROLES)

    def _setup_mocks(self):
        self._setup_mock_remotesession()
        self._setup_mock_usermanager()

    def _setup_mock_remotesession(self):
        self._get_source_update_env_dict.return_value = UPDATE_ENV_DICT
        self._execute_command_in_target.side_effect = self._execute_side_effect

    @property
    def _get_source_update_env_dict(self):
        return self._mock_remotesession_factory.return_value.get_source_update_env_dict

    @property
    def _execute_command_in_target(self):
        return self._mock_remotesession_factory.return_value.execute_command_in_target

    @staticmethod
    def _execute_side_effect(command):
        assert command == 'cat /etc/userconfig/user_config.yaml'
        with open(USER_CONFIG_PATH) as f:
            return RunResult(status=0, stdout=f.read(), stderr='')

    def _setup_mock_usermanager(self):
        def mock_create_user_with_roles(*roles):
            roles_list = list(roles)
            assert list(roles_list) == ROLES, (
                'Expected {expected!r}, actual {actual!r}'.format(
                    expected=ROLES,
                    actual=roles_list))
            return USERRECORD

        self._mock_usermanager.create_user_with_roles.side_effect = mock_create_user_with_roles

    def verify_create(self):
        self._assert_target_dict(self._envcreator.create(target=TARGET,
                                                         envname=self._envname))
        self._verify_mock_calls()

    def verify_multiple_creates(self):
        self.verify_create()
        self._assert_target_dict(self._envcreator.create(target='target2',
                                                         envname=self._envname))
        self._get_source_update_env_dict.assert_called_once_with(
            self._openrc, target=TARGET)

    def verify_create_admin(self):
        assert self._envcreator.create(target=TARGET, envname='admin') == UPDATE_ENV_DICT
        self._verify_mock_calls()

    def verify_create_um_admin(self):
        assert self._envcreator.create(target=TARGET, envname='um_admin') == UM_ADMIN_ENV_DICT

    def _assert_target_dict(self, target_dict):
        assert target_dict == self._expected_target_dict, (
            'Expcted: {expected}, actual: {actual}'.format(
                expected=self._expected_target_dict,
                actual=target_dict))

    @property
    def _expected_target_dict(self):
        d = UPDATE_ENV_DICT.copy()
        d.update({'OS_USERNAME': USERRECORD.username,
                  'OS_PASSWORD': USERRECORD.password,
                  'OS_TENANT_NAME': 'infrastructure',
                  'OS_PROJECT_NAME': 'infrastructure'})
        return d

    def _verify_mock_calls(self):
        self._get_source_update_env_dict.assert_called_once_with(
            self._openrc, target=TARGET)

    @property
    def _openrc(self):
        return 'openrc'
