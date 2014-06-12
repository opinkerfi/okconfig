# !/usr/bin/env python
"""Test adding objects"""

import os.path
import sys


# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest2 as unittest
import okconfig
from pynag import Model
import tests


class Host(tests.OKConfigTest):
    """Tests pertaining to addhost"""

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
        okconfig.addhost('www.okconfig.org', group_name="multigroup")
        okconfig.addhost('okconfig.org', group_name="multigroup")

        hosts = Model.Host.objects.filter(contact_groups="multigroup")
        self.assertEqual(len(hosts), 2)

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


if __name__ == "__main__":
    unittest.main()