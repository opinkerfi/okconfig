#
# Copyright 2011, Pall Sigurdsson <palli@opensource.is>
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" This module provides helper functions for okconfig """

from __future__ import absolute_import
from __future__ import print_function
from builtins import object
import re
import fcntl
import os
from subprocess import Popen, PIPE, STDOUT

from pynag import Model

import okconfig


def add_defaultservice_to_host(host_name):
    """ Given a specific hostname, add default service to it """
    # Get our host
    try: my_host = Model.Host.objects.get_by_shortname(host_name)
    except ValueError: raise okconfig.OKConfigError("Host %s not found." % host_name)

    # Dont do anything if file already exists
    service = Model.Service.objects.filter(name=host_name)
    if len(service) != 0:
        return False

    # Make sure that host belongs to a okconfig-compatible group
    hostgroup_name = my_host['hostgroups'] or "default"
    hostgroup_name = hostgroup_name.strip('+')
    if hostgroup_name in okconfig.get_groups():
        GROUP=hostgroup_name
    else:
        GROUP='default'

    template = default_service_template
    template = re.sub("HOSTNAME", host_name, template)
    template = re.sub("GROUP", GROUP, template)
    fh = open( my_host['filename'], 'a')
    fh.write(template)
    fh.close()
    return True


def group_exists(group_name):
    """ Check if a servicegroup,contactgroup or hostgroups exist with shortname == group_name

    Returns:
        False if no groups are found, otherwise it returns a list of groups
    """
    servicegroups = Model.Servicegroup.objects.filter(shortname=group_name)
    contactgroups = Model.Contactgroup.objects.filter(shortname=group_name)
    hostgroups = Model.Hostgroup.objects.filter(shortname=group_name)
    result = (servicegroups+contactgroups+hostgroups)
    if result == ([]):
        return False
    return result

def runCommand(command):
    """runCommand: Runs command from the shell prompt.

     Arguments:
         command: string containing the command line to run
     Returns:
         stdout/stderr of the command run
     Raises:
         BaseException if returncode > 0
    """
    proc = Popen(command, shell=True, stdin=PIPE,stdout=PIPE,stderr=PIPE,)
    stdout, stderr = proc.communicate('through stdin to stdout')
    result = proc.returncode,stdout,stderr
    if proc.returncode > 0:
        error_string = "* Could not run command (return code= %s)\n" % proc.returncode
        error_string += "* Error was:\n%s\n" % (stderr.strip())
        error_string += "* Command was:\n%s\n" % command
        error_string += "* Output was:\n%s\n" % (stdout.strip())
        if proc.returncode == 127: # File not found, lets print path
            path=os.getenv("PATH")
            error_string += "Check if y/our path is correct: %s" % path
        raise okconfig.OKConfigError( error_string )
    else:
        return result


class clientInstall(object):
    import okconfig.config
    def __init__(self,
                 script=okconfig.config.nsclient_installfiles + "/install_nsclient.sh",
                 script_args=None,
                 merge_env=None):
        """
        Initializes the object for nsclient installs

        :param host_name: hostname of machine to install on
        :param domain:    windows domain, use '.' for local domain
        :param username:  username with privileges to install
        :param password:  yeah, the password
        """
        self.process = None
        self.unparseable_lines = []
        self.stage_state = {}
        self.script = script
        self.script_args = script_args
        self.current_stage = None
        self.merge_env = merge_env

    def execute(self):
        """
        Executes the install_nsclient command which installs the nsclient agent for windows machines
        """

        user_env = os.environ
        if self.merge_env:
            user_env.update(self.merge_env)

        if not self.script_args:
            self.script_args = []

        try:
            self.process = Popen([self.script] + self.script_args,
                                 env=user_env,
                                 stdout=PIPE,
                                 stderr=STDOUT,
                                 bufsize=1,
                                 shell=False
            )

            # Make stdout non blocking
            fd = self.process.stdout.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        except Exception as e:
            raise okconfig.OKConfigError(e)

    def get_state(self):
        """
        Checks if there is any output from the script and parses it
        return the state of each install stage
        """
        import re

        while True:
            self.process.stdout.flush()
            line = ""
            try:
                line = self.process.stdout.readline()
            except IOError:
                break
            if not line:
                break
            m = re.match("^\[(.*?)\s*\] (\S+?) (.*)$", line)
            if m:
                self.stage_state[m.group(1)] = m.group(3)
                self.current_stage = m.group(1)
            else:
                self.unparseable_lines.append(line)
        return self.current_stage, self.stage_state


default_service_template = '''
# This is a template service for HOSTNAME
# Services that belong to this host should use this as a template
define service {
        name                            HOSTNAME
        use                             GROUP-default_service
        host_name                       HOSTNAME
        contact_groups                  +GROUP
        service_groups                  +GROUP
        service_description             Default Service for HOSTNAME
        register                        0
}
'''

if __name__ == '__main__':
    print(add_defaultservice_to_host('host1'))
