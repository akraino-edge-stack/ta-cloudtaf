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
import pytest
import mock
from crl.remotesession.remotesession import RemoteSession
from hostcli import HostCli
from .clusterverifier import (
    Type1Verifier,
    Type2Verifier,
    ClusterMocks)
from .userverifier import UserVerifier
from .envcreatorverifier import EnvCreatorVerifier
from . import cluster
from . import usermanager
from .envcreator import EnvCreator


@pytest.fixture(params=[Type1Verifier,
                        Type2Verifier])
def clusterverifier(request, clustermocks):
    return request.param(clustermocks)


@pytest.fixture
def clustermocks(mock_remotesession, mock_hostcli, mock_envcreator, mock_usermanager):
    return ClusterMocks(remotesession=mock_remotesession,
                        hostcli=mock_hostcli,
                        envcreator=mock_envcreator,
                        usermanager=mock_usermanager)


@pytest.fixture
def mock_remotesession():
    with mock.patch.object(cluster,
                           'RemoteSession',
                           mock.create_autospec(RemoteSession)) as p:
        yield p


@pytest.fixture
def mock_hostcli():
    with mock.patch.object(cluster,
                           'HostCli',
                           mock.create_autospec(HostCli)) as p:
        yield p


@pytest.fixture
def mock_envcreator():
    with mock.patch.object(cluster,
                           'EnvCreator',
                           mock.create_autospec(EnvCreator)) as p:
        yield p


@pytest.fixture
def mock_usermanager():
    with mock.patch.object(cluster,
                           'UserManager',
                           mock.create_autospec(usermanager.UserManager)) as p:
        yield p


@pytest.fixture(params=['Role', 'Role-Name'])
def userverifier(request):
    return UserVerifier(role_attr=request.param)


@pytest.fixture
def envcreatorverifier():
    return EnvCreatorVerifier()
