# !/usr/bin/env python
"""Test templates"""

import os.path
import sys


# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest2 as unittest
import okconfig
from pynag import Model
import tests


class Template(tests.OKConfigTest):
    """Template additions tests"""

    def setUp(self):
        super(Template, self).setUp()

        okconfig.addhost("www.okconfig.org")
        okconfig.addhost("okconfig.org")
        okconfig.addhost("aliased.okconfig.org",
                         address="192.168.1.1",
                         group_name="testgroup")


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

if __name__ == "__main__":
    unittest.main()