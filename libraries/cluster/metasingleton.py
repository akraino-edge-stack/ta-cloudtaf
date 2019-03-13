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


class MetaSingleton(type):
    instance_attr = '__instance'

    def __call__(cls, *args, **kwargs):
        if MetaSingleton.instance_attr not in cls.__dict__:
            setattr(cls,
                    MetaSingleton.instance_attr,
                    super(MetaSingleton, cls).__call__(*args, **kwargs))
        return getattr(cls, MetaSingleton.instance_attr)

    def clear(cls):
        if MetaSingleton.instance_attr in cls.__dict__:
            delattr(cls, MetaSingleton.instance_attr)
