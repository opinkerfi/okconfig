#!/usr/bin/env python
import os
import sys

# Make sure we import from working tree
okconfig_base = os.path.dirname(os.path.realpath(__file__ + "/.."))
sys.path.insert(0, okconfig_base)

import unittest2 as unittest
import doctest

from tests import tests_dir

import okconfig

def load_tests(loader=None, tests=None, pattern=None):
    suite = unittest.TestSuite()

    # Add doctesting
    suite.addTest(doctest.DocTestSuite(okconfig))

    # Load unit tests from all files starting with test_*
    for all_test_suite in unittest.defaultTestLoader.discover(
            '.',
            pattern='test_*.py'):
        for test_suite in all_test_suite:
            suite.addTest(test_suite)
    return suite

if __name__ == "__main__":
    unittest.main()






