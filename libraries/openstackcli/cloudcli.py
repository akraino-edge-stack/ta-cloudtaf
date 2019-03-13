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
import six
from .cliwrapperbase import CliWrapperBase


@six.add_metaclass(abc.ABCMeta)  # pylint: disable=abstract-method
class CloudCliBase(CliWrapperBase):

    @property
    def _target_kwargs(self):
        return {'target': '{prebase}{os_cloud}.{cloudname}'.format(
            prebase=self._prebase,
            os_cloud=self._os_cloud,
            cloudname=self._cloudname)}

    @property
    def _os_cloud(self):
        return 'os-cloud'

    @property
    def _prebase(self):
        return (''
                if self._expected_target == 'default' else
                '{}.'.format(self._expected_target))

    @property
    def _cloudname(self):
        return 'cloudname'

    @property
    def _expected_cmd_args(self):
        return ' --os-cloud {} '.format(self._cloudname)


class TargetCloud(CloudCliBase):

    @property
    def _expected_target(self):
        return 'target'


class DefaultCloud(CloudCliBase):

    @property
    def _expected_target(self):
        return 'default'


class TypoCloud(CloudCliBase):

    @property
    def _expected_target(self):
        return 'target.{os_cloud}.{cloudname}'.format(
            os_cloud=self._os_cloud,
            cloudname=self._cloudname)

    @property
    def _prebase(self):
        return 'target.'

    @property
    def _os_cloud(self):
        return 'typo-cloud'

    @property
    def _expected_cmd_args(self):
        return ' --os-cloud default '
