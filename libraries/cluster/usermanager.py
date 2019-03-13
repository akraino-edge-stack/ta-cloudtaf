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

from collections import namedtuple
from .usergen import UserGen

INITIAL_PASSWORD = 'intl_AM10srt'
PASSWORD = 'um_UM0scrt'


class UserRecord(namedtuple('UserRecord', ['uuid',
                                           'username',
                                           'password',
                                           'roles'])):

    def create_with_password(self, password):
        d = self._asdict().copy()
        d.update({'password': password})
        return UserRecord(**d)


class UserManagerError(Exception):
    pass


class UserManager(object):

    _target = 'default.um_admin'
    _all_roles = 'all_roles'
    _no_roles = 'no_roles'
    _special_roles = [_all_roles, _no_roles]
    _basic_member = 'basic_member'
    _linux_user = 'linux_user'

    def __init__(self, hostcli_factory):
        self._hostcli_factory = hostcli_factory
        self._hostcli_inst = None
        self._roles_users = dict()
        self._roles_cache = set()
        self._user_gen_inst = None

    def create_user_with_roles(self, *roles):
        r = self._get_and_verify_roles(roles)

        key = self._get_roles_users_key(r)
        if key not in self._roles_users:
            self._roles_users[key] = self._create_with_roles(r)
            self._change_password(roles)

        return self._roles_users[key]

    def delete_users(self):
        """Delete all users created by :meth:`.create_user_with_roles`.
        """
        for _, userrecord in self._roles_users.items():
            self._hostcli.run_raw('user delete {}'.format(userrecord.uuid),
                                  target=self._target)

    def get_user_and_set_password(self, *roles):
        """Get user with INITIAL_PASSWORD and set password to PASSWORD.

        .. note::

           This method should be called only by :class:`cluster.envcreator.EnvCreator`.
        """
        upd_roles = self._get_roles(roles)
        key = self._get_roles_users_key(upd_roles)
        old_userrecord = self._roles_users[key]
        self._roles_users[key] = old_userrecord.create_with_password(PASSWORD)
        return old_userrecord

    @staticmethod
    def _get_roles_users_key(roles):
        return frozenset(roles)

    @property
    def _hostcli(self):
        if self._hostcli_inst is None:
            self._hostcli_inst = self._hostcli_factory()
        return self._hostcli_inst

    def _get_uuid(self, username):
        users = self._hostcli.run('user list', target=self._target)
        for u in users:
            if u['User-Name'] == username:
                return u['User-ID']

        raise UserManagerError('User {} does not exist in target'.format(username))

    def _get_and_verify_roles(self, roles):
        self._verify_special_roles(roles)
        r = self._get_roles(roles)
        self._verify_roles(r)
        return r

    def _verify_special_roles(self, roles):
        if len(roles) == 1:
            return

        for special_role in self._special_roles:
            if special_role in roles:
                raise UserManagerError(
                    'Special role {special_role!r} and other roles in {roles}'.format(
                        special_role=special_role,
                        roles=roles))

    def _get_roles(self, roles):
        if set(roles) == set([self._all_roles]):
            return self._roles
        if set(roles) == set([self._no_roles]):
            return []
        return roles

    def _verify_roles(self, roles):
        given_roles = set(roles)
        if len(roles) > len(given_roles):
            raise UserManagerError('Duplicate roles in {}'.format(roles))
        target_roles = set(self._roles)
        notexisting = given_roles - target_roles
        if notexisting:
            raise UserManagerError('Roles {} not found'.format(notexisting))

    def _create_with_roles(self, roles):
        username = self._user_gen.create_username(roles)
        uuid = self._create_user_from_user(username, roles)
        return UserRecord(uuid=uuid,
                          username=username,
                          password=INITIAL_PASSWORD,
                          roles=roles)

    def _create_user_from_user(self, username, roles):
        self._hostcli.run_raw('user create {username} '
                              '--email user@email.me '
                              '--password {password}'.format(
                                  username=username,
                                  password=INITIAL_PASSWORD), target=self._target)
        uuid = self._get_uuid(username)
        for role in roles:
            self._hostcli.run_raw('user add role {uuid} {role}'.format(uuid=uuid,
                                                                       role=role),
                                  target=self._target)
        return uuid

    def _change_password(self, roles):
        self._hostcli.run_raw(
            'user set password --opassword {old} --npassword {new}'.format(
                old=INITIAL_PASSWORD,
                new=PASSWORD),
            target='default.set_password:{}'.format(','.join(roles)))

    @property
    def _user_gen(self):
        if self._user_gen_inst is None:
            self._user_gen_inst = UserGen(len(self._roles))
        return self._user_gen_inst

    @property
    def _roles(self):
        if not self._roles_cache:
            self._roles_cache = self._get_roles_via_hostcli()
        return self._roles_cache

    def _get_roles_via_hostcli(self):
        roles = self._hostcli.run('role list all', target=self._target)
        role_attr = 'Role-Name' if 'Role-Name' in roles[0] else 'Role'
        return [role[role_attr] for role in roles
                if role[role_attr] not in [self._basic_member, self._linux_user]]
