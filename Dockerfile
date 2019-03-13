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
FROM fedora:26

RUN [ -z ${HTTP_PROXY:+x} ] || echo proxy=${HTTP_PROXY} >> /etc/dnf/dnf.conf

RUN dnf install -y \
python-pip \
libffi-devel \
gcc \
openssl-libs \
openssl \
redhat-rpm-config \
python-devel \
openssl-devel \
python3-tox \
openssh-clients \
git \
iputils \
graphviz
