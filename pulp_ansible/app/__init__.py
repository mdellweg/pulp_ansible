from pulpcore.plugin import PulpPluginAppConfig


class PulpAnsiblePluginAppConfig(PulpPluginAppConfig):
    """
    Entry point for pulp_ansible plugin.
    """

    name = "pulp_ansible.app"
    label = "ansible"
    version = "0.19.1.dev"
    python_package_name = "pulp-ansible"
