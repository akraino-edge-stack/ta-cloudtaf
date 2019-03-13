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


def test_create_user_with_roles(userverifier):
    userverifier.verify_create_user_with_roles()


def test_delete_users(userverifier):
    userverifier.verify_delete_users()


def test_corrupted_user_list(userverifier):
    userverifier.verify_corrupted_user_list()


def test_user_with_roles_raises(userverifier):
    userverifier.verify_user_with_roles_notexist()


def test_user_roles_duplicates(userverifier):
    userverifier.verify_user_roles_duplicates()


def test_one_user_per_roles(userverifier):
    userverifier.verify_one_user_per_roles()


def test_all_roles(userverifier):
    userverifier.verify_all_roles()


def test_no_roles(userverifier):
    userverifier.verify_no_roles()


def test_special_roles_raises(userverifier):
    userverifier.verify_special_roles_raises()
