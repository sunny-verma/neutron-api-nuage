# Copyright 2019 Nuage Networks by Nokia
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
from charmhelpers.core.hookenv import (
    log,
)
# This charm's library contains all of the handler code associated with
# sdn_charm
import charm.openstack.neutron_api_nuage as neutron_api_nuage  # noqa
import subprocess

charm.use_defaults(
    'charm.installed',
    'config.changed',
    'update-status')


def exec_cmd(cmd=None, error_msg='Command exited with ERROR', fatal=False):
    '''
    Function to execute any bash command on the node.
    '''
    if cmd is None:
        log("No command specified")
    else:
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            log(error_msg)


@reactive.when('neutron-plugin-api-subordinate.connected')
@reactive.when_not('config.neutron_conf_rendered')
def configure_plugin(api_principle):
    with charm.provide_charm_instance() as neutron_api_nuage_charm:
        neutron_api_nuage_charm.configure_plugin(api_principle)
        neutron_api_nuage_charm.assess_status()
    reactive.set_state('config.neutron_conf_rendered')


@reactive.when('neutron-plugin-api-subordinate.connected')
def render_config(*args):
    with charm.provide_charm_instance() as neutron_api_nuage_charm:
        neutron_api_nuage_charm.render_with_interfaces(args)
        neutron_api_nuage_charm.assess_status()
    reactive.set_state('config.ml2_rendered')

@reactive.when('config.ml2_rendered')
@reactive.when_not('db.synced')
def db_migration():
    log("Migrating database now")
    exec_cmd(cmd=['neutron-db-manage', 'upgrade', 'heads'],
             error_msg="db-manage command executed with errors", fatal=False)
    log("Migrating database done")
    reactive.set_state('db.synced')
    reactive.set_state('neutron.restart')


@reactive.when_file_changed(neutron_api_nuage.ML2_CONF)
def file_changed():
    reactive.set_state('neutron.restart')

@reactive.when('neutron-plugin-api-subordinate.connected')
@reactive.when('neutron.restart')
def remote_restart(api_principle):
    api_principle.request_restart()
    reactive.remove_state('neutron.restart')
