#!/usr/bin/env python
"""Test adding objects"""

import os.path
import sys
from shutil import copytree

# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest
import okconfig
from pynag.Utils.misc import FakeNagiosEnvironment
from pynag import Model

class Host(unittest.TestCase):
    """Tests pertaining to addhost"""
    def setUp(self):
        environment = FakeNagiosEnvironment()
        environment.create_minimal_environment()
        copytree(os.path.realpath("../usr/share/okconfig/templates"),
                   environment.tempdir + "/conf.d/okconfig-templates")
        environment.update_model()

        self.environment = environment

        self._okconfig_overridden_vars = {}
        for var in ['nagios_config', 'destination_directory',
                    'examples_directory', 'examples_directory_local']:
            self._okconfig_overridden_vars[var] = getattr(okconfig, var)

        okconfig.nagios_config = self.environment.get_config().cfg_file
        okconfig.destination_directory = self.environment.objects_dir
        okconfig.examples_directory = "../usr/share/okconfig/examples"
        okconfig.examples_directory_local = environment.tempdir + "/okconfig"

        os.mkdir(okconfig.examples_directory_local)

    def tearDown(self):
        self.environment.terminate()
        for var, value in self._okconfig_overridden_vars.items():
            setattr(okconfig, var, value)

    def test_basic(self):
        """Basic addition of host"""
        okconfig.addhost('okconfig.org')

        hosts = Model.Host.objects.filter(host_name='okconfig.org')
        self.assertTrue(len(hosts) == 1)
        self.assertEqual(hosts[0].use, "okc-default-host")
        self.assertEqual(hosts[0].contact_groups, "default")
        self.assertEqual(hosts[0].hostgroups, "default")

        filename = hosts[0].get_filename()
        self.assertEqual(filename.split('/')[-2], 'default')

    def test_group(self):
        """Addition of host within a specific group

        It should automatically create the group
        """
        okconfig.addhost('okconfig.org', group_name='testgroup')

        hosts = Model.Host.objects.filter(host_name='okconfig.org')

        self.assertTrue(len(hosts) == 1)
        self.assertEqual(hosts[0].use, "okc-default-host")
        self.assertEqual(hosts[0].contact_groups, "testgroup")
        self.assertEqual(hosts[0].hostgroups, "testgroup")

        filename = hosts[0].get_filename()
        self.assertEqual(filename.split('/')[-2], 'testgroup')

    def test_conflict(self):
        """Try to add a host that already exists"""
        okconfig.addhost('okconfig.org')

        self.assertRaises(okconfig.OKConfigError,
                          okconfig.addhost, 'okconfig.org')

    def test_template(self):
        """Add a host with a template"""
        okconfig.addhost('okconfig.org', templates=['linux'])

        services = [s.use for s in Model.Service.objects.filter(
            host_name='okconfig.org')]
        for template in ['okc-linux-check_disks',
                         'okc-linux-check_load']:
            self.assertTrue(template in services)

    def test_multiple_to_group(self):
        """Add 2 hosts to a group"""
        okconfig.addhost('www.okconfig.org')
        okconfig.addhost('okconfig.org')

        hosts = Model.Host.objects.filter(host_name__contains="okconfig.org")
        self.assertTrue(len(hosts) == 2)

    def test_address(self):
        """Add a host with an address"""
        okconfig.addhost('www.okconfig.org', address="192.168.1.1")

        hosts = Model.Host.objects.filter(host_name="www.okconfig.org")
        self.assertTrue(len(hosts) == 1)
        self.assertEqual(hosts[0].address, "192.168.1.1")

    def test_alias(self):
        """Add a host with an alias"""
        okconfig.addhost('www.okconfig.org', alias="The alias host")

        hosts = Model.Host.objects.filter(host_name="www.okconfig.org")
        self.assertTrue(len(hosts) == 1)
        self.assertEqual(hosts[0].alias, "The alias host")

    def test_force(self):
        """Test force adding a host"""
        okconfig.addhost('www.okconfig.org')

        self.assertRaises(okconfig.OKConfigError, okconfig.addhost,
                          'www.okconfig.org')

class Template(unittest.TestCase):
    """Template additions tests"""
    def setUp(self):
        environment = FakeNagiosEnvironment()
        environment.create_minimal_environment()
        copytree(os.path.realpath("../usr/share/okconfig/templates"),
                   environment.tempdir + "/conf.d/okconfig-templates")
        environment.update_model()

        self.environment = environment

        self._okconfig_overridden_vars = {}
        for var in ['nagios_config', 'destination_directory',
                    'examples_directory', 'examples_directory_local']:
            self._okconfig_overridden_vars[var] = getattr(okconfig, var)

        okconfig.nagios_config = self.environment.get_config().cfg_file
        okconfig.destination_directory = self.environment.objects_dir
        okconfig.examples_directory = "../usr/share/okconfig/examples"
        okconfig.examples_directory_local = environment.tempdir + "/okconfig"

        os.mkdir(okconfig.examples_directory_local)

        okconfig.addhost("www.okconfig.org")
        okconfig.addhost("okconfig.org")
        okconfig.addhost("aliased.okconfig.org",
                         address="192.168.1.1",
                         group_name="testgroup")


    def tearDown(self):
        self.environment.terminate()
        for var, value in self._okconfig_overridden_vars.items():
            setattr(okconfig, var, value)

    def test_basic(self):
        """Add a template to a host"""
        okconfig.addtemplate("www.okconfig.org", template_name="http")

        services = Model.Service.objects.filter(
            host_name="www.okconfig.org",
            use="okc-check_http",
            service_description="HTTP www.okconfig.org")

        self.assertEquals(len(services), 1, "There can be only one")

    def test_multiple(self):
        """Add multiple templates to a host"""
        okconfig.addtemplate('www.okconfig.org', template_name="http")
        okconfig.addtemplate('www.okconfig.org', template_name="linux")

        for use, description in [
            ('okc-check_http', 'HTTP www.okconfig.org', ),
            ('okc-linux-check_disks', 'Disk Usage', ),
            ('okc-linux-check_load', 'Load', ),
            ('okc-linux-check_swap', 'Swap Usage', ),
        ]:
            services = Model.Service.objects.filter(
                host_name="www.okconfig.org",
                use=use,
                service_description=description)
            self.assertEqual(1, len(services), "Unable to match %s %s" % (
                use, description))

    def test_conflict(self):
        """Add conflicting template"""
        okconfig.addtemplate('www.okconfig.org', template_name="http")

        self.assertRaises(okconfig.OKConfigError,
                          okconfig.addtemplate,
                          host_name='www.okconfig.org',
                          template_name='http')

    def test_force(self):
        """Test force adding a template"""
        okconfig.addtemplate('www.okconfig.org', template_name="http")
        okconfig.addtemplate('www.okconfig.org', template_name="http",
                             force=True)

    def test_group(self):
        """Test adding template with group"""
        okconfig.addtemplate("aliased.okconfig.org",
                             "http",
                             group_name="webgroup")

        services = Model.Service.objects.filter(
            host_name="aliased.okconfig.org",
            service_description="HTTP aliased.okconfig.org",
        )
        self.assertEqual(1, len(services), "There can be only one")
        self.assertEqual(services[0].contact_groups, "webgroup")

class Group(unittest.TestCase):
    """Template additions tests"""
    def setUp(self):
        environment = FakeNagiosEnvironment()
        environment.create_minimal_environment()
        copytree(os.path.realpath("../usr/share/okconfig/templates"),
                   environment.tempdir + "/conf.d/okconfig-templates")
        environment.update_model()

        self.environment = environment

        self._okconfig_overridden_vars = {}
        for var in ['nagios_config', 'destination_directory',
                    'examples_directory', 'examples_directory_local']:
            self._okconfig_overridden_vars[var] = getattr(okconfig, var)

        okconfig.nagios_config = self.environment.get_config().cfg_file
        okconfig.destination_directory = self.environment.objects_dir
        okconfig.examples_directory = "../usr/share/okconfig/examples"
        okconfig.examples_directory_local = environment.tempdir + "/okconfig"

        os.mkdir(okconfig.examples_directory_local)

        okconfig.addhost("www.okconfig.org")
        okconfig.addhost("okconfig.org")
        okconfig.addhost("aliased.okconfig.org",
                         address="192.168.1.1",
                         group_name="testgroup")


    def tearDown(self):
        self.environment.terminate()
        for var, value in self._okconfig_overridden_vars.items():
            setattr(okconfig, var, value)

    def test_basic(self):
        """Add a group"""
        okconfig.addgroup("testgroup1")

        contacts = Model.Contactgroup.objects.filter(
            contactgroup_name='testgroup1'
        )

        self.assertEqual(1, len(contacts), 'There can be only one')

        hostgroups = Model.Hostgroup.objects.filter(
            hostgroup_name='testgroup1'
        )
        self.assertEqual(1, len(hostgroups), 'There can be only one')

    def test_alias(self):
        """Add a group with an alias"""
        okconfig.addgroup("testgroup1", alias="the first testgroup")

        contacts = Model.Contactgroup.objects.filter(
            contactgroup_name='testgroup1',
            alias='the first testgroup')
        self.assertEqual(1, len(contacts))

    def test_conflict(self):
        """Test adding a conflicting group"""
        okconfig.addgroup("testgroup1")

        self.assertRaises(okconfig.OKConfigError,
                          okconfig.addgroup,
                          "testgroup1")

    def test_force(self):
        """Test force adding a group"""
        okconfig.addgroup("testgroup1")
        okconfig.addgroup("testgroup1", force=True)


if __name__ == "__main__":
    unittest.main()
