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


class Contact(tests.OKConfigTest):
    def test_basic(self):
        """Add a contact"""
        okconfig.addcontact("testcontact")

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact'
        )
        self.assertEqual(1, len(contacts), 'There can be only one')

    def test_alias(self):
        """Add contact with alias"""
        okconfig.addcontact('testcontact', alias="Test Contact")

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact',
            alias='Test Contact'
        )
        self.assertEqual(1, len(contacts), 'There can be only one')
        self.assertEqual('Test Contact', contacts[0].alias)

    def test_force(self):
        """Add contact overwriting a previous one"""
        okconfig.addcontact('testcontact', 'Should be replaced')
        okconfig.addcontact('testcontact', 'With this one', force=True)

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact',
        )
        self.assertEqual(1, len(contacts), 'There can be only one')
        self.assertEqual('With this one', contacts[0].alias)

    def test_conflict(self):
        """Make sure we raise on conflict"""
        okconfig.addcontact('testcontact', 'should be ok')
        self.assertRaises(okconfig.OKConfigError, okconfig.addcontact,
                          'testcontact', 'but this one not')

    def test_withgroup(self):
        """Make a contact within a group"""
        okconfig.addcontact('testcontact', group_name='testinggroup')

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact')

        self.assertEqual(1, len(contacts), 'There can be only one')
        self.assertEqual('testinggroup', contacts[0].contactgroups)

    def test_email(self):
        """Contact with email"""
        okconfig.addcontact('testcontact', email="testing@okconfig.org")

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact')

        self.assertEqual(1, len(contacts), 'There can be only one')
        self.assertEqual('testing@okconfig.org', contacts[0].email)

    def test_use(self):
        """Contact with use statement"""
        okconfig.addcontact('testcontact', use="okc-contact")

        contacts = Model.Contact.objects.filter(
            contact_name='testcontact')

        self.assertEqual(1, len(contacts), 'There can be only one')
        self.assertEqual('okc-contact', contacts[0].use)

if __name__ == "__main__":
    unittest.main()