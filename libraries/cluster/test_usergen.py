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

from .usergen import UserGen


def test_create_with_no_roles():
    u = UserGen(3)
    assert u.create_username([]) == 'no_roles'


def test_create_with_all_roles():
    u = UserGen(3)
    assert u.create_username(['role{}'.format(i) for i in range(3)]) == 'all_roles'


def test_create_with_some_roles():
    u = UserGen(3)
    roles = ['role1', 'role0']
    assert u.create_username(roles) == 'role00'
    assert u.create_username(roles) == 'role01'
