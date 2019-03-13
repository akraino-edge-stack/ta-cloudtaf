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


class UserGen(object):

    def __init__(self, roles_len):
        self._roles_len = roles_len
        self._usergens = {}

    def create_username(self, roles):
        if not roles:
            return 'no_roles'
        if len(roles) == self._roles_len:
            return 'all_roles'
        return next(self._get_user_gen(sorted(roles)[0]))

    def _get_user_gen(self, base):
        if base not in self._usergens:
            self._usergens[base] = self._user_gen(base)
        return self._usergens[base]

    @staticmethod
    def _user_gen(base):
        for idx in itertools.count():  # pragma: no branch
            yield '{base}{idx}'.format(base=base, idx=idx)
