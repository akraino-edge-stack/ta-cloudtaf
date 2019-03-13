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

BASIC_MEMBER = 'basic_member'

LINUX_USER = 'linux_user'

ROLES = ['role{}'.format(i) for i in range(4)]


class UserTuple(namedtuple('UserTuple', ['uuid',
                                         'username',
                                         'email',
                                         'password',
                                         'roles'])):
    def __hash__(self):
        d = self._asdict().copy()
        d['roles'] = sorted(d['roles'])
        return hash(repr(sorted(d.items())))


class User(object):
    def __init__(self, username, email='user@email.me', password=None):
        self.username = username
        self.email = email
        self._password = password
        self.added_roles = set([])
        self._uuid = None
        self._password_history = [self.password]

    def set_password(self, password):
        self._password = password
        self._password_history.append(password)

    @property
    def password(self):
        return self._password

    @property
    def password_history(self):
        return self._password_history

    @property
    def uuid(self):
        return self._uuid if self._uuid else 'UUID_{}'.format(self.username)

    def set_uuid(self, uuid):
        self._uuid = uuid

    def set_added_roles(self, roles):
        self.added_roles = set(roles)

    def add_role(self, role):
        assert role not in self.roles, 'Role {role} already in {username}'.format(
            role=role,
            username=self.username)
        self.added_roles.add(role)

    @property
    def roles(self):
        return self.added_roles.union(set([BASIC_MEMBER]))

    def __repr__(self):
        return str(self.usertuple)  # pragma: no cover

    def __eq__(self, other):
        return self.usertuple == other

    def __hash__(self):
        return hash(self.usertuple)

    @property
    def usertuple(self):
        return UserTuple(uuid=self.uuid,
                         username=self.username,
                         email=self.email,
                         password=self.password,
                         roles=self.roles)


class HandlerError(Exception):
    pass


@six.add_metaclass(abc.ABCMeta)
class HandlerBase(object):
    def __init__(self, users):
        self._users = users

    def handle(self, cmd, target):
        self._handle_target(target)

        if not cmd.startswith(self._expected_startswith):
            raise HandlerError()

        return self._handle(cmd.split())

    @abc.abstractmethod
    def _handle_target(self, target):
        """Handle target

        Raises:
            HandlerError: if target cannot be handled by handler
        """

    @abc.abstractproperty
    def _expected_startswith(self):
        """Return the expected start of the command.
        """

    @abc.abstractmethod
    def _handle(self, args):
        """Handle and return the command

        Raises:
           HandlerError: if command cannot be handled by handler
        """


class SetPasswordHandler(HandlerBase):
    """Handler for HostCli command
    user set password --opassword OPASSWORD --npassword NPASSWORD
    """
    def __init__(self, users, envcreator):
        super(SetPasswordHandler, self).__init__(users)
        self._envcreator = envcreator
        self._envname = None

    @property
    def _expected_startswith(self):
        return 'user set password'

    def _handle_target(self, target):
        if not target.startswith('default.set_password:'):
            raise HandlerError()
        self._envname = target.split('.')[1]

    def _handle(self, args):
        pwds = self._get_passwords(args)
        openrc_dict = self._envcreator.create(target='default', envname=self._envname)
        assert pwds.old == openrc_dict['OS_PASSWORD'], (pwds.old,
                                                        openrc_dict['OS_PASSWORD'])
        user = self._get_user_for_openrc_dict(openrc_dict)
        assert pwds.old == user.password
        user.set_password(pwds.new)
        return 'Your password has been changed.'

    @staticmethod
    def _get_passwords(args):
        assert args[3] == '--opassword'
        assert args[5] == '--npassword'
        p = Passwords(old=args[4], new=args[6])
        assert p.old != p.new, p
        return p

    def _get_user_for_openrc_dict(self, openrc_dict):
        username = openrc_dict['OS_USERNAME']
        for _, user in self._users.items():
            if user.username == username:
                return user

        raise AssertionError('User {} not found'.format(username))  # pragma: no cover


class Passwords(namedtuple('Passwords', ['old', 'new'])):
    pass


class AdminHandlerBase(HandlerBase):  # pylint: disable=abstract-method
    def _handle_target(self, target):
        if target != 'default.um_admin':
            raise HandlerError()


class UserCreateHandler(AdminHandlerBase):
    @property
    def _expected_startswith(self):
        return 'user create'

    def _handle(self, args):
        assert args[3] == '--email'
        assert args[5] == '--password'
        user = User(username=args[2],
                    email=args[4],
                    password=args[6])
        assert user.uuid not in self._users, 'User {} already created'.format(user)
        self._users[user.uuid] = user
        return 'User created. The UUID is {uuid}'.format(uuid=user.uuid)


class UserListHandler(AdminHandlerBase):
    @property
    def _expected_startswith(self):
        return 'user list'

    def _handle(self, args):
        return [{'Password-Expires': None,
                 'User-ID': u.uuid,
                 'Enabled': True,
                 'User-Name': u.username} for _, u in self._users.items()]


class UserDeleteHandler(AdminHandlerBase):
    @property
    def _expected_startswith(self):
        return 'user delete'

    def _handle(self, args):
        assert len(args) == 3, 'Wrong number of arguments for delete {}'.format(args)
        del self._users[args[2]]
        return 'User deleted.'


class CorruptedUserListHandler(UserListHandler):
    def _handle(self, args):
        return []


class UserAddRoleHandler(AdminHandlerBase):
    @property
    def _expected_startswith(self):
        return 'user add role'

    def _handle(self, args):
        self._users[args[3]].add_role(args[4])
        return 'Role has been added to the user.'


class RoleListAllHandler(AdminHandlerBase):
    def __init__(self, users, role_attr):
        super(RoleListAllHandler, self).__init__(users)
        self._role_attr = role_attr

    @property
    def _expected_startswith(self):
        return 'role list all'

    def _handle(self, args):
        assert len(args) == 3, 'Expected: {expected}, actual {actual}'.format(
            expected=self._expected_startswith.split(),
            actual=args)
        return [{'Role-Description': 'Role Description {}'.format(role),
                 'Chroot': False,
                 'Is-Service-Role': True,
                 self._role_attr: role} for role in self._roles]

    @property
    def _roles(self):
        return ROLES + [BASIC_MEMBER, LINUX_USER]


class Handlers(object):  # pylint: disable=too-few-public-methods
    def __init__(self, handlers):
        self._handlers = handlers

    def handle(self, cmd, target):
        for h in self._handlers:
            try:
                return h.handle(cmd=cmd, target=target)
            except HandlerError:
                pass

        assert 0, 'User Command {!r} not found'.format(cmd)  # pragma: no cover


class FakeHostCliUser(object):
    def __init__(self, mock_hostcli, role_attr):
        self._mock_hostcli = mock_hostcli
        self._role_attr = role_attr
        self._envcreator = None
        self._users = {}
        self._run_raw_handlers = None
        self._run_handlers = None

    def set_envcreator(self, envcreator):
        self._envcreator = envcreator

    def initialize(self):
        self._run_raw_handlers = self._create_handlers(UserCreateHandler,
                                                       UserAddRoleHandler,
                                                       UserDeleteHandler,
                                                       self._create_set_password_handler)
        self._run_handlers = self._create_handlers(UserListHandler,
                                                   self._create_role_handler)
        self._set_side_effects()

    @property
    def users(self):
        return set([u for _, u in self._users.items()])

    def get_user(self, user_id):
        return self._users[user_id]

    def set_corrupted_user_list(self):
        self._run_handlers = self._create_handlers(CorruptedUserListHandler,
                                                   self._create_role_handler)

    def _create_role_handler(self, users):
        return RoleListAllHandler(users, role_attr=self._role_attr)

    def _create_set_password_handler(self, users):
        return SetPasswordHandler(users, envcreator=self._envcreator)

    def _create_handlers(self, *handler_factories):
        return Handlers([h(self._users) for h in handler_factories])

    def _set_side_effects(self):
        self._mock_hostcli.return_value.run.side_effect = self._run
        self._mock_hostcli.return_value.run_raw.side_effect = self._run_raw

    def _run_raw(self, cmd, target):
        return self._run_raw_handlers.handle(cmd, target=target)

    def _run(self, cmd, target):
        return self._run_handlers.handle(cmd, target=target)
