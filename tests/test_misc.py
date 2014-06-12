# !/usr/bin/env python
"""Test adding objects"""

import os.path
import sys


# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest2 as unittest
import okconfig
import tests


class Verify(tests.OKConfigTest):
    """Test okconfig verification routines"""

    def test_valid(self):
        """Is the overall configuration valid"""
        self.assertTrue(okconfig.is_valid())

    def test_invalid_main_config(self):
        """Is the nagios config there and writable"""
        okconfig.nagios_config = "invalid"
        self.assertFalse(okconfig.is_valid())

    def test_invalid_okconfig_template_dir(self):
        """Is the okconfig template directory valid"""
        okconfig.template_directory = "invalid"
        self.assertFalse(okconfig.is_valid())

    def test_invalid_okconfig_destination_directory(self):
        """Is the destination directory and parent writable"""
        okconfig.destination_directory = "invalid"
        self.assertFalse(okconfig.is_valid())

class Misc(unittest.TestCase):
    def test_path_checker(self):
        """Check if executables are in path"""
        self.assertTrue(okconfig._is_in_path("true"))
    def test_path_checker_not_found(self):
        """Check if executables are not in path"""
        self.assertFalse(okconfig._is_in_path("okconfig-this-not-exist"))


if __name__ == "__main__":
    unittest.main()
