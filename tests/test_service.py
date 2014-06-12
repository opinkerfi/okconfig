# !/usr/bin/env python
"""Test adding objects"""

import os.path
import sys


# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest2 as unittest
import tests

class Service(tests.OKConfigTest):
    """Test service functionality"""

    def tearDown(self, test=None):
        pass
    def test_basic(self):
        """Test basic service addition"""

        # TODO: need to review functionality
        """
        okconfig.addservice("okc-mysql-check_connection-time",
                            host_name="linux.okconfig.org",
                            service_description="maria conntime")
        service = Model.Service.objects.filter(host_name="linux.okconfig.org",
                                     service_description="maria conntime")
        """
        return

if __name__ == "__main__":
    unittest.main()
