import socket
import subprocess

import charmhelpers.core.hookenv as hookenv
import charmhelpers.contrib.network.ip as ch_ip
import charms_openstack.charm
import charmhelpers.contrib.openstack.utils as ch_utils
import charms_openstack.adapters
from charmhelpers.fetch.ubuntu import import_key
from charmhelpers.fetch import (
    apt_install,
    add_source,
    apt_update,
)
ML2_DIR = '/etc/neutron/plugins/ml2/'
ML2_CONF = ML2_DIR + 'ml2_conf.ini'
VXLAN = 'vxlan'
NUAGE_PACKAGES = ['nuage-openstack-neutron', 'nuage-openstack-neutronclient']


@charms_openstack.charm.register_os_release_selector
def choose_charm_class():
    """Choose the charm class based on the neutron-common package installed"""
    return ch_utils.os_release('neutron-common')


class QueensNeutronApiNuageCharm(charms_openstack.charm.OpenStackCharm):

    # Internal name of charm
    service_name = name = 'neutron-api-nuage'

    # First release supported
    release = 'queens'

    # List of packages to install for this charm
    packages = NUAGE_PACKAGES
    restart_map = {ML2_CONF: ['neutron-server']}
    adapters_class = charms_openstack.adapters.OpenStackRelationAdapters

    # required_relations = ['neutron-plugin-api-subordinate']

    service_plugins = hookenv.config('nuage-service-plugins')

    @property
    def neutron_user(self):
        return self.user

    @property
    def neutron_group(self):
        return self.group

    def configure_plugin(self, api_principle):
        """Add sections and tuples to insert values into neutron-server's
        neutron.conf
        """
        inject_config = {
            "neutron-api": {
                "/etc/neutron/neutron.conf": {
                    "sections": {
                        'DEFAULT': [
                        ]
                    }
                }
            }
        }

        api_principle.configure_plugin(
            neutron_plugin='vsp',
            core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
            neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
            service_plugins=self.service_plugins,
            subordinate_configuration=inject_config)

    def install(self):
        """install

        Install hook is run when the charm is first deployed on a node.
        """
        
        import_key(hookenv.config('extra-key'))
        add_source(hookenv.config('extra-source'))
        apt_update()
        pkgs = NUAGE_PACKAGES
        for pkg in pkgs:
            apt_install(pkg, options=['--force-yes',
                                      '--allow-unauthenticated'], fatal=True)

    user = 'root'
    group = 'neutron'
