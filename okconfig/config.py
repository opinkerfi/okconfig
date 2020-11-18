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

""" This module provides access to default configuration values in /etc/okconfig.conf """

from __future__ import absolute_import
from builtins import str
import os

# This is the main configuration file
config_file             = "/etc/okconfig.conf"

# First some default values, in case config does not specify any
nagios_config           = "/etc/nagios/nagios.cfg"
template_directory      = "/etc/nagios/okconfig/templates"
examples_directory      = "/etc/nagios/okconfig/examples"
destination_directory   = "/etc/nagios/okconfig/"
install_nrpe_script     = "/usr/share/okconfig/client/linux/install_okagent.sh"
nsclient_installfiles   = "/usr/share/okconfig/client/windows/"
examples_directory_local= destination_directory + "/examples"
git_commit_changes      = "1"
try:
    if os.path.isfile(config_file):
        for line in open(config_file).readlines():
            line = line.strip()
            if line.startswith('#'): continue
            line = line.split(None,1)
            if len(line) != 2: continue
            keyword = str(line[0]).strip()
            value = str(line[1]).strip()
            if keyword   == "nagios_config": nagios_config = value
            elif keyword == "template_directory": template_directory = value
            elif keyword == "examples_directory": examples_directory = value
            elif keyword == "destination_directory": destination_directory = value
            elif keyword == "install_nrpe_script": install_nrpe_script = value
            elif keyword == "nsclient_installfiles": nsclient_installfiles = value
            elif keyword == "examples_directory_local": examples_directory_local = value
            elif keyword == "git_commit_changes": git_commit_changes = value
except ImportError:
    raise
