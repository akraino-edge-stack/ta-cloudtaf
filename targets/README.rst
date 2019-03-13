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

Targets
=======

The target.ini files are copied by rfcli-docker script to this
directory.

.. note:

   The target.ini files are not stored to git.


Target.ini files
----------------

The content of the target.ini files follows::

   [target]
   IP:     <Management VIP of target>
   USER:   <Admin user>
   PASS:   <Admin password>

Target.ini files profiles properties 2019-Mar-26
------------------------------------------------

Currently CaaS is not deployed and so neither caas_master nor caas_worker
service profiles exists. To solve this problem, additional properties
for such targets has to be added::

   [target]
   IP:     <Management VIP of target>
   USER:   <Admin user>
   PASS:   <Admin password>
   MASTER_PROFILE: management
   WORKER_PROFILE: base
