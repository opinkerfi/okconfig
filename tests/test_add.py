#!/usr/bin/env python
"""Test adding objects"""

import os.path
import sys


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
        environment.update_model()
        self.environment = environment

        okconfig.nagios_config = self.environment.get_config().cfg_file
        okconfig.destination_directory = self.environment.objects_dir
        okconfig.examples_directory = "../usr/share/okconfig/examples"
        okconfig.examples_directory_local = environment.tempdir + "/okconfig"
        os.mkdir(okconfig.examples_directory_local)

    def tearDown(self):
        #self.environment.terminate()
        pass

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
        okconfig.addhost('addressed.okconfig.org', address="192.168.1.1")

        host = Model.Host.objects.filter(host_name="addressed.okconfig.org")[0]
        self.assertEqual(host.address, "192.168.1.1")


if __name__ == "__main__":
    unittest.main()
