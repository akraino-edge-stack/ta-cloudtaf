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

from crl.interactivesessions.shells.sudoshell import BashShell
from .clusterverifier import CorruptedVerifier
from .cluster import Cluster
from . import cluster


def test_get_host(clusterverifier):
    clusterverifier.verify_get_host()


def test_master_external_ip(clusterverifier):
    clusterverifier.verify_master_external_ip()


def test_get_hosts_with_profile(clusterverifier):
    clusterverifier.verify_get_hosts_with_profiles()


def test_get_hosts_containing(clusterverifier):
    clusterverifier.verify_hosts_containing()


def test_cluster_caching(clusterverifier):
    clusterverifier.verify_cluster_config_caching()


def test_cluster_singleton():
    assert Cluster() == Cluster()


def test_cluster_mgmt_shelldicts(clusterverifier):
    clusterverifier.verify_mgmt_shelldicts()


def test_get_host_raises(clustermocks):
    c = CorruptedVerifier(clustermocks)
    c.verify_corrupted_raises()


def test_create_remotesession(clusterverifier):
    clusterverifier.verify_create_remotesession()


def test_initialize_remotesession(clusterverifier):
    clusterverifier.verify_initialize_remotesession()


def test_create_hostcli(clusterverifier):
    clusterverifier.verify_create_hostcli()


def test_initialize_hostcli(clusterverifier):
    clusterverifier.verify_initialize_hostcli()


def test_create_user_with_roles(clusterverifier):
    clusterverifier.verify_create_user_with_roles()


def test_delete_users(clusterverifier):
    clusterverifier.verify_delete_users()


def test_envcreator_usage(clusterverifier):
    clusterverifier.verify_envcreator()


def test_sudoshell_in_cluster():
    assert cluster.BashShell == BashShell


def test_is_dpdk(clusterverifier):
    clusterverifier.verify_is_dpdk()


def test_get_hosts_with_dpdk(clusterverifier):
    clusterverifier.verify_get_hosts_with_dpdk()
