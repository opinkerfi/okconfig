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

from __future__ import absolute_import
from __future__ import print_function
from builtins import object
import subprocess
import socket
from pynag import Model
from .helper_functions import runCommand
import okconfig

class ScannedHost(object):
    """Simple datastructure for a recently portscanned host"""
    def __init__(self, ipaddress=None, hostname=None,ismonitored=None):
        self.ipaddress = ipaddress
        self.hostname = hostname
        self.ismonitored = ismonitored
        if hostname is None:
            self.hostname = self.get_hostname()
    def check(self):
        """Runs all self.ch*. Returns nothing"""

        if self.is_windows():
            self.platform = "Windows"
        elif self.is_linux():
            self.platform = "Linux"
        else:
            self.platform = "Unknown"

        if self.is_agent_okconfig():
            self.nrpe = "OKconfig agent"
        elif self.is_agent_responding():
            self.nrpe = "Generic NRPE running"
        elif self.is_agent_installed():
            self.nrpe = "NRPE running but does not respond to us"
        else:
            self.nrpe = "NRPE Not detected"

        if self.has_webserver():
            self.port80 = "yes"
        else:
            self.port80 = "no"

    def get_hostname(self):
        """returns hostname given a specific ip address"""
        try:
            name= socket.gethostbyaddr(self.ipaddress)
            return name[0]
        except Exception:
            return None
    def is_windows(self):
        """Returns true if machine replies on port 3389"""
        return check_tcp(host=self.ipaddress, port=3389)
    def is_agent_installed(self):
        """Returns True if nrpe client is running"""
        return check_tcp(host=self.ipaddress, port=5666)
    def is_linux(self):
        """Returns true if machine replies on port 22"""
        return check_tcp(host=self.ipaddress, port=22)
    def has_webserver(self):
        """Returns true if machine replies on port 80"""
        return check_tcp(host=self.ipaddress, port=80)
    def has_mssql(self):
        """Returns true if machine replies on port 1433"""
        return check_tcp(host=self.ipaddress, port=1433)
    def has_nrpe(self):
        """Returns true if machine replies on port 5666"""
        return check_tcp(host=self.ipaddress, port=5666)
    def has_ssl(self):
        """Returns true if machine replies on port 443"""
        return check_tcp(host=self.ipaddress, port=443)

    def is_agent_responding(self):
        """returns true if host responds to check_nrpe commands"""
        returncode, stdout, stderr = runCommand("check_nrpe -H '%s'" % self.ipaddress)
        if returncode == 0:
            return True
        if returncode == 1:
            return False
        return None
    def is_agent_okconfig(self):
        """returns true if host responds to check_nrpe commands"""
        returncode,stdout,stderr = runCommand("check_nrpe -H '%s' -c get_disks")
        if returncode == 0: return True
        if returncode == 1: return False
        return None
def check_tcp(host="localhost", port=22, timeout=5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect( (host, port) )
        #s.send('')
        #s.recv(1024)
        s.close()
        return True
    except Exception:
        #raise e
        return False

def runCommand(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,)
    stdout, stderr = proc.communicate('through stdin to stdout')
    returncode = proc.returncode
    return returncode,stdout,stderr


def get_ip_address_list():
    """returns a list of every ip address of every host in nagios"""
    hosts = Model.Host.objects.all
    result = []
    for host in hosts:
        a = host['address']
        if not a is None and a not in result:
            result.append(a)
    return result

def check_nrpe(host):
    command = "check_nrpe -H '%s'" % host

def get_my_ip_address():
    """Returns default ip address of this host"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('94.142.154.11', 80))
    return s.getsockname()[0]

def pingscan(network='192.168.1.0/24'):
    """scans a specific network, returns a list of all ip that respond"""
    command =  "fping -t 50 -i 10 -a "
    if network.find('/') > 0: command += " -g "
    command += network
    r,stdout,stderr = runCommand(command)
    if r > 1:
        raise Exception("Error running %s: %s" % (command,stderr) )
    ip_list = []
    for i in stdout.split('\n'):
        try: socket.inet_aton(i)
        except Exception: continue
        ip_list.append(i)
    return ip_list

def get_new_hosts(network='192.168.1.0/24'):
    """Returns a list of ScannedHost alive in given network that do not exist in nagios"""
    registered_ips = get_ip_address_list()
    new_hosts =[]
    for i in get_all_hosts(network=network):
        if not i.ipaddress in registered_ips:
            new_hosts.append(i)
    return new_hosts

def get_all_hosts(network='192.168.1.0/24'):
    """Returns a list of ScannedHost alive in given network"""
    scanned_ips = pingscan(network)
    registered_ips = get_ip_address_list()
    all_hosts = []
    for i in scanned_ips:
            ismonitored = i in registered_ips
            host = ScannedHost(ipaddress=i,ismonitored=ismonitored)
            all_hosts.append( host)
    return all_hosts

def get_hostname(self):
    """returns hostname given a specific ip address"""
    try:
        name= socket.gethostbyaddr(self.ipaddress)
        return name[0]
    except Exception:
        return None

def traceroute(host="localhost"):
    """ Returns a list of every host discovered while tracerouting

    Returns:
        ["ip1","ip2","ip3",...]
    """
    result = []
    returncode,stdout,stderr = runCommand("traceroute -n '%s'" % host)
    print(stdout)
    if returncode > 0:
        raise okconfig.OKConfigError("Failed to traceroute host %s, error: %s" % (host, stderr))
    for line in stdout.split("\n"):
        line = line.split()
        if len(line) < 2:
            continue
        if line[0].isdigit():
            result.append(line[1])
    return result

def set_network_parents(host_name, method="traceroute"):
    """ Autocreates network parents for a given host """
    if method == 'traceroute':
        parents = traceroute(host=host_name)
        print(len(parents), "parents found")
        previous_host = None
        for i in parents:
            hosts = Model.Host.objects.filter(address=i)
            if len(hosts) == 0:
                print("adding host ", i)
                dnsname = get_hostname(i)
                if dnsname is None:
                    dnsname = i
                okconfig.addhost(host_name=dnsname, address=i)
                hosts = Model.Host.objects.filter(address=i)
            host = hosts[0]
            if previous_host is not None:
                print(previous_host.address, "->", host.address)
                host.parents = previous_host.host_name
                host.save()
            previous_host = host


if __name__ == '__main__':
    print(set_network_parents('mbl.is'))