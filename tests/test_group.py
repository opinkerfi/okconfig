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


class Group(tests.OKConfigTest):
    """Template additions tests"""

    def setUp(self):
        super(Group, self).setUp()

        okconfig.addhost("www.okconfig.org")
        okconfig.addhost("okconfig.org")
        okconfig.addhost("aliased.okconfig.org",
                         address="192.168.1.1",
                         group_name="testgroup")


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