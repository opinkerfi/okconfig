import os

tests_dir = os.path.dirname(os.path.realpath(__file__)) or '.'
os.chdir(tests_dir)

_okconfig_overridden_vars = {}
_environment = None
import okconfig
import okconfig.config as config
from shutil import copytree
import unittest2 as unittest

from pynag.Utils.misc import FakeNagiosEnvironment


class OKConfigTest(unittest.TestCase):
    def setUp(self, test=None):
        """
        Sets up the nagios fake environment and overrides okconfig configuration
        variables to make changes within it.
        """
        global _environment
        _environment = FakeNagiosEnvironment()
        _environment.create_minimal_environment()
        copytree(os.path.realpath("../usr/share/okconfig/templates"),
                 _environment.tempdir + "/conf.d/okconfig-templates")
        _environment.update_model()

        for var in ['nagios_config', 'destination_directory',
                    'examples_directory', 'examples_directory_local',
                    'template_directory']:
            _okconfig_overridden_vars[var] = getattr(okconfig, var)

        okconfig.nagios_config = _environment.get_config().cfg_file
        config.nagios_config = okconfig.nagios_config
        config.git_commit_changes = 0
        okconfig.destination_directory = _environment.objects_dir
        okconfig.examples_directory = "../usr/share/okconfig/examples"
        okconfig.template_directory = "../usr/share/okconfig/templates"
        okconfig.examples_directory_local = _environment.tempdir + "/okconfig"

        os.mkdir(okconfig.examples_directory_local)


        okconfig.addhost("linux.okconfig.org",
                         address="192.168.1.1",
                         templates=["linux"])
        okconfig.addhost("windows.okconfig.org",
                         address="192.168.1.2",
                         templates=["windows"])
        okconfig.addhost("webserver.okconfig.org",
                         address="192.168.1.2",
                         templates=["http"])

    def tearDown(self, test=None):
        """
        Tear down the fake nagios environment and restore okconfig variables
        """
        _environment.terminate()
        for var, value in _okconfig_overridden_vars.items():
            setattr(okconfig, var, value)

    def runTest(*args, **kwargs):
        pass
