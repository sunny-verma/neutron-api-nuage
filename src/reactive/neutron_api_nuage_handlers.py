# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import charms_openstack.charm as charm
import charms.reactive as reactive

# This charm's library contains all of the handler code associated with
# sdn_charm
import charm.openstack.neutron_api_nuage as neutron_api_nuage  # noqa

charm.use_defaults(
    'charm.installed',
    'config.changed',
    'update-status')


@reactive.when('neutron-plugin-api-subordinate.connected')
def render_config(*args):
    with charm.provide_charm_instance() as neutron_api_nuage_charm:
        neutron_api_nuage_charm.render_with_interfaces(args)
        neutron_api_nuage_charm.assess_status()

@reactive.when('neutron-plugin-api-subordinate.connected')
def configure_plugin(api_principle):
    with charm.provide_charm_instance() as neutron_api_nuage_charm:
        neutron_api_nuage_charm.configure_plugin(api_principle)
        neutron_api_nuage_charm.assess_status()
    api_principle.request_restart()

@reactive.when_file_changed(neutron_api_nuage.ML2_CONF)
@reactive.when('neutron-plugin-api-subordinate.connected')
def remote_restart(api_principle):
    api_principle.request_restart()
