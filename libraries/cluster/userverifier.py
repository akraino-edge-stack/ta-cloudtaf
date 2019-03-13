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

import itertools
import mock
import pytest
from crl.remotesession.remotesession import RemoteSession
from hostcli import HostCli
from .usermanager import (
    UserManager,
    UserManagerError,
    PASSWORD,
    INITIAL_PASSWORD)
from .envcreator import EnvCreator
from .testutils.fakehostcli import (
    FakeHostCliUser,
    User,
    ROLES)
from .usergen import UserGen


class UserVerifier(object):
    def __init__(self, role_attr):
        self._mock_hostcli_factory = mock.create_autospec(HostCli)
        self._mock_remotesession_factory = mock.create_autospec(RemoteSession)
        self._hostcliuser = FakeHostCliUser(self._mock_hostcli_factory,
                                            role_attr=role_attr)
        self._usermanager = UserManager(self._mock_hostcli_factory)
        self._envcreator = EnvCreator(
            remotesession_factory=self._mock_remotesession_factory,
            usermanager=self._usermanager)
        self._usergen = None
        self._initialize()

    def _initialize(self):
        self._setup_remotesession()
        self._setup_hostcliuser()
        self._setup_usergen()

    def _setup_remotesession(self):
        g = self._mock_remotesession_factory.return_value.get_source_update_env_dict
        g.return_value = {}

    def _setup_hostcliuser(self):
        self._hostcliuser.set_envcreator(self._envcreator)
        self._hostcliuser.initialize()

    def _setup_usergen(self):
        self._usergen = UserGen(len(ROLES))

    def verify_create_user_with_roles(self):
        for roles in self._roles_gen():
            actual_user = self._get_actual_user(
                self._usermanager.create_user_with_roles(*roles))
            expected_user = self._get_expected_user(roles)
            for actual in [actual_user, self._hostcliuser.get_user(expected_user.uuid)]:
                assert actual_user == expected_user, (
                    'expected {expected}, actual {actual}'.format(
                        expected=expected_user,
                        actual=actual))
                self._assert_password_history(actual_user.uuid)

    def verify_delete_users(self):
        self.verify_create_user_with_roles()
        self._usermanager.delete_users()
        assert not self._hostcliuser.users

    def verify_corrupted_user_list(self):
        self._hostcliuser.set_corrupted_user_list()
        with pytest.raises(UserManagerError) as excinfo:
            self._usermanager.create_user_with_roles(*ROLES)

        assert str(excinfo.value) == 'User all_roles does not exist in target'

    def verify_user_with_roles_notexist(self):
        notexists = ['notexists']
        with pytest.raises(UserManagerError) as excinfo:
            self._usermanager.create_user_with_roles(ROLES[0], *notexists)

        msg = str(excinfo.value)
        assert msg == 'Roles {} not found'.format(set(notexists)), msg

    def verify_user_roles_duplicates(self):
        duplicates = (ROLES[0], ROLES[1], ROLES[0])
        with pytest.raises(UserManagerError) as excinfo:
            self._usermanager.create_user_with_roles(*duplicates)

        msg = str(excinfo.value)
        assert msg == 'Duplicate roles in {}'.format(duplicates), msg

    def verify_one_user_per_roles(self):
        users_list = []
        for _ in range(2):
            self._setup_usergen()
            self.verify_create_user_with_roles()
            users_list.append(self._hostcliuser.users)

        assert users_list[0] == users_list[1], users_list

    def verify_all_roles(self):
        userrecord = self._usermanager.create_user_with_roles('all_roles')
        user = self._hostcliuser.get_user(userrecord.uuid)
        assert user.username == 'all_roles', user.username
        assert user.added_roles == set(ROLES)

    def verify_no_roles(self):
        userrecord = self._usermanager.create_user_with_roles('no_roles')
        user = self._hostcliuser.get_user(userrecord.uuid)
        assert user.username == 'no_roles', user.username
        assert not user.added_roles

    def verify_special_roles_raises(self):
        for special_role in ['no_roles', 'all_roles']:
            with pytest.raises(UserManagerError) as excinfo:
                roles = (special_role, ROLES[0])
                self._usermanager.create_user_with_roles(*roles)

            msg = str(excinfo.value)
            assert msg == 'Special role {special_role!r} and other roles in {roles}'.format(
                special_role=special_role,
                roles=roles), msg

    @staticmethod
    def _get_actual_user(user):
        u = User(username=user.username, password=user.password)
        u.set_added_roles(user.roles)
        u.set_uuid(user.uuid)
        return u

    def _get_expected_user(self, roles):
        user = User(username=self._usergen.create_username(roles),
                    password=PASSWORD)
        user.set_added_roles(roles)
        return user

    @staticmethod
    def _roles_gen():
        for r in range(len(ROLES) + 1):
            for roles in itertools.combinations(ROLES, r):
                yield roles

    def _assert_password_history(self, user_id):
        user = self._hostcliuser.get_user(user_id)
        actual_history = user.password_history
        expected_history = [INITIAL_PASSWORD, PASSWORD]
        assert actual_history == expected_history, (
            'Expected {expected}, actual {actual}'.format(
                expected=expected_history,
                actual=actual_history))
