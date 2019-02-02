import socket
import subprocess

import charmhelpers.core.hookenv as hookenv
import charmhelpers.contrib.network.ip as ch_ip
import charms_openstack.charm
import charms_openstack.adapters
from charmhelpers.fetch import (
    apt_install,
    add_source,
    apt_update,
)

ML2_CONF = '/etc/neutron/plugins/ml2_conf.ini'
VXLAN = 'vxlan'
NUAGE_PACKAGES = ['nuage-openstack-neutron', 'nuage-openstack-neutronclient']


class NeutronApiNuageCharm(charms_openstack.charm.OpenStackCharm):

    # Internal name of charm
    service_name = name = 'neutron-api-nuage'

    # First release supported
    release = 'queens'

    # List of packages to install for this charm
    packages = NUAGE_PACKAGES

    required_relations = ['neutron-plugin-api-subordinate']

    service_plugins = 'NuagePortAttributes,NuageAPI,NuageL3'

    def configure_plugin(self, api_principle):
        """Add sections and tuples to insert values into neutron-server's
        neutron.conf
        """
        inject_config = {
            "neutron-api": {
                "/etc/neutron/neutron.conf": {
                    "sections": {
                        'DEFAULT': [
                        ],
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
        '''
        Install hook is run when the charm is first deployed on a node.
        '''
        add_source(hookenv.config('extra-source'), hookenv.config('extra-key'))
        apt_update()
        pkgs =NUAGE_PACKAGES
        for pkg in pkgs:
            apt_install(pkg, options=['--force-yes', '--allow-unauthenticated'], fatal=True)

