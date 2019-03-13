..
    Copyright 2019 Nokia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Introduction
------------

Test cases are executed within a virtual environment in order to have all
python package dependencies installed. This virtual environment creation is
managed by tox. Furthermore tox execution can be optionally wrapped with a
docker environment to provide required operating system packages and
configuration to pull dependencies.

Execution environment as simple diagram::

  $ ./rfcli-docker <args> == [ docker [ tox [ virtualenv [ rfcli -> robotframework <args> ] ] ] ]

You can find here more details about how to execute in your machine here
(windows specific, but it contains tips also if you have linux):
:ref:`windowsinstructions`


Writing robot test cases
------------------------
Please use the following tags mentioned here:
:ref:`taggingpolicy` and also consider our test case design guidelines:
:ref:`designguidelines`


Execution examples
------------------

Docker + tox::

  $ ./rfcli-docker -t path/to/target.ini -s smoke-tests testcases/

This is the most simple way to execute the cloudtaf2 tests. As docker is being
used the created python virtual environment as well as the resulting files will
be owned by the "root" and not the actual user. Additionally initial execution
will take some time to build the image.

You may also run directly *rfcli* environment with *tox*::

  $ tox -e rfcli -- -t path/to/target.ini -s smoke-tests testcases


Execution examples - tox only
-----------------------------

This is more lightweight way to execute the tests but requires certain
operating system packages to be installed first. Please see the "Dockerfile"
for installed packages.

Tox only - more lightweight for those who know what they are doing::

  $ tox -e rfcli -- -t path/to/target.ini -s smoke-tests testcases/

Virtual environment
-------------------

Python virtual environment is created with requirements.txt. All python
packages must be set to certain versions in order to execute tests the same way
with older builds as they have been initially executed.

To update the frozen versions to the latest, execute::

  $ tox -e freeze

To add more packages, update the requirements-minimal.txt and execute::

  $ tox -e freeze

You can add specific version requirements to the requirements-minimal.txt
to make sure that they are used in the generated frozen requirements.txt.

The recommendation is that the frozen requirements.txt file is not edited
directly but always via the requirements-minimal.txt changes and via this freeze
generation.

In clear cases you can also update requirements.txt directly. However,
in this case, please make sure that::

  $ tox --recreate -e check-requirements

is succesful. This tool checks that the requirements-minimal.txt
is consistent with the requirements.txt and that all requirements in
requirements.txt can be really installed.
installed.


Rebuild docker image
--------------------

Rebuild docker image manually e.g. when changing the Dockerfile contents::

  $ ./rfcli-docker-build

Unit testing
------------

Unit tests can be executed with::

  $ tox

Running Docker behind a proxy
-----------------------------
The 'dnf install' -command requires a proxy setting when Docker is running
behind a proxy.

The Dockerfile writes the proxy information to /etc/dnf/dnf.conf -file when
HTTP_PROXY argument is set as a --build-arg. For example::

 # docker build --build-arg HTTP_PROXY=http://10.1.2.3:8080/
