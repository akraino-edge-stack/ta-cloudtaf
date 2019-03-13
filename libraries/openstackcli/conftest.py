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

# pylint: disable=redefined-outer-name
from collections import namedtuple

import pytest
from .openstackcli import (
    OpenStack,
    Runner)


from .cloudcli import (
    DefaultCloud,
    TargetCloud,
    TypoCloud)

from .envcli import (
    EnvCli,
    InitializedEnvCli)


CLIWRAPPER_CLSES = [DefaultCloud,
                    TargetCloud,
                    TypoCloud,
                    EnvCli,
                    InitializedEnvCli]


CLI_CLSES = [OpenStack, Runner]


class WrapperCliTuple(namedtuple('WrapperCliTuple', ['wrapper', 'cli'])):
    pass


@pytest.fixture(params=[WrapperCliTuple(wrapper=cliw, cli=clicls)
                        for clicls in CLI_CLSES
                        for cliw in CLIWRAPPER_CLSES])
def cliwrapper(mock_remotesession, request):
    c = request.param.wrapper(request.param.cli)
    c.set_remotesession(mock_remotesession)
    c.initialize()
    return c


class MethodFmt(namedtuple('MethodFormat', ['method', 'fmt'])):
    pass


@pytest.fixture(params=['run', 'run_ignore_output'])
def methodfmt(request, openstack):
    return {
        'run': MethodFmt(openstack.run, ' -f json'),
        'run_ignore_output': MethodFmt(openstack.run_ignore_output, '')}[
            request.param]
