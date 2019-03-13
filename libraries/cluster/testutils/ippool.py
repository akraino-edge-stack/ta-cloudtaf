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


class IPPool(object):
    def __init__(self):
        self._internal_ip = self._ip_gen(base='192.168.1')
        self._external_ip = self._ip_gen(base='10.1.1')

    def get_internal_ip(self):
        return next(self._internal_ip)

    def get_external_ip(self):
        return next(self._external_ip)

    @staticmethod
    def _ip_gen(base):
        for i in itertools.count(start=2):  # pragma: no branch
            yield '{base}.{i}'.format(base=base, i=i)
