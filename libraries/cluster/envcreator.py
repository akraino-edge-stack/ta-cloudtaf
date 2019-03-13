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
import yaml
from crl.remotesession.envcreatorbase import EnvCreatorBase


class EnvCreator(EnvCreatorBase):
    _openrc = 'openrc'

    def __init__(self, remotesession_factory, usermanager):
        self._remotesession_factory = remotesession_factory
        self._usermanager = usermanager
        self._openrc_dict_cache = None
        self._um_admin_creds_cache = None

    def create(self, target, envname):
        openrc_dict = self._get_openrc_dict(target)
        if envname.startswith('set_password:'):
            self._set_password_and_update_dict(envname, openrc_dict)
        elif envname == 'um_admin':
            self._update_openrc_dict_um_admin(openrc_dict)
        elif envname != 'admin':
            self._create_user_and_update_dict(envname, openrc_dict=openrc_dict)

        return openrc_dict

    @property
    def _um_admin_creds(self):
        if self._um_admin_creds_cache is None:
            self._setup_um_admin_creds_cache()
        return self._um_admin_creds_cache

    def _set_password_and_update_dict(self, envname, openrc_dict):
        roles = self._get_roles_for_envname(envname)
        userrecord = self._usermanager.get_user_and_set_password(*roles)
        self._update_openrc_dict(openrc_dict, userrecord)

    @staticmethod
    def _get_roles_for_envname(envname):
        r = envname.split(':')[1]
        return [role.strip() for role in r.split(',')] if r else []

    @staticmethod
    def _update_openrc_dict(openrc_dict, userrecord):
        openrc_dict.update({'OS_USERNAME': userrecord.username,
                            'OS_PASSWORD': userrecord.password,
                            'OS_TENANT_NAME': 'infrastructure',
                            'OS_PROJECT_NAME': 'infrastructure'})

    def _update_openrc_dict_um_admin(self, openrc_dict):
        openrc_dict.update({'OS_USERNAME': self._um_admin_creds.username,
                            'OS_PASSWORD': self._um_admin_creds.password,
                            'OS_TENANT_NAME': 'infrastructure',
                            'OS_PROJECT_NAME': 'infrastructure'})

    def _create_user_and_update_dict(self, envname, openrc_dict):
        roles = [role.strip() for role in envname.split(',')]
        userrecord = self._usermanager.create_user_with_roles(*roles)
        self._update_openrc_dict(openrc_dict, userrecord)

    def _get_openrc_dict(self, target):
        remotesession = self._remotesession_factory()
        if self._openrc_dict_cache is None:
            self._openrc_dict_cache = (
                remotesession.get_source_update_env_dict(self._openrc,
                                                         target=target))
        return self._openrc_dict_cache.copy()

    def _setup_um_admin_creds_cache(self):
        rem = self._remotesession_factory()
        res = rem.execute_command_in_target('cat /etc/userconfig/user_config.yaml')
        u = yaml.load(res.stdout, Loader=yaml.Loader)
        users = u['users']
        self._um_admin_creds_cache = Credentials(username=users['initial_user_name'],
                                                 password=users['initial_user_password'])


class Credentials(namedtuple('Credentials', ['username', 'password'])):
    pass
