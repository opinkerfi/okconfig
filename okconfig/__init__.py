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

"""This module provides an interface to okconfig utilities
and operations such as adding new hosts to Nagios or adding
templates to current hosts

Example Usage:

import okconfig
okconfig.nagios_config="/etc/nagios/nagios.cfg"
okconfig.addhost("myhost.example.com", group_name="databases", templates=["linux","mysql"]) 
"""

from __future__ import absolute_import
__author__ = "Pall Sigurdsson"
__copyright__ = "Copyright 2011, Pall Sigurdsson"
__credits__ = ["Pall Sigurdsson"]
__license__ = "GPL"
__version__ = "1.3.5"
__maintainer__ = "Gardar Thorsteinsson"
__email__ = "gardar@ok.is"
__status__ = "Development"


import socket
import os
try:
    import paramiko
except ImportError:
    paramiko = None

import pynag.Model
import pynag.Utils

from . import network_scan
from . import config
from . import helper_functions

nagios_config = config.nagios_config
template_directory =config.template_directory
examples_directory= config.examples_directory
examples_directory_local= config.examples_directory_local
destination_directory = config.destination_directory
pynag.Model.pynag_directory = destination_directory

required_gateways = []

pynag.Model.cfg_file = config.nagios_config

version = __version__
def is_valid():
    """Checks if okconfig is installed and properly configured.

    Returns True/False

    See verify() for more details
    """
    checks = verify()
    for result in list(checks.values()):
        if result is False: return False
    return True

def _is_in_path(command):
    """ Searches $PATH and returns true if command is found, and in path """


    is_executable = lambda x: os.path.isfile(x) and os.access(x, os.X_OK)

    if command.startswith('/'):
        return is_executable(command)

    my_path = os.environ['PATH'].split(':')
    for possible_path in my_path:
        full_path = "%s/%s" % (possible_path,command)
        if is_executable(full_path): return True
    return False


def verify():
    """Checks if okconfig is installed and properly configured.

    Returns dict of {'check_name':Boolean}

    Check if:
    1) nagios_config exists
    2) template_directory exists
    3) destination_directory exists (and is writable)
    """
    results = {}

    # 1) nagios_config exists
    check = "Main configuration file %s is readable" % nagios_config
    results[check] = os.access(nagios_config, os.R_OK)

    # 2) template_directory exists
    check = "template_directory %s exists" % template_directory
    results[check] = os.access(template_directory, os.R_OK) and os.path.isdir(template_directory)

    # 3) destination_directory or parent exists (and is writable)
    for ddir in [destination_directory, "%s/.." % destination_directory]:
        ddir = os.path.dirname(ddir)
        check = "destination_directory %s is writable" % ddir
        results[check] = os.access(ddir, os.W_OK + os.R_OK) and os.path.isdir(ddir)
        if results[check] == True: break

    # 4)
    # Should no longer be need
    # TODO: Remove this commented codeblock
    #okconfig_binaries = ('addhost','findhost','addgroup','addtemplate')
    #for command in okconfig_binaries:
    #	check = "'%s' command is in path" % command
    #	results[check] = _is_in_path(command)

    return results

def addhost(host_name, address=None, group_name=None, templates=None, use=None, alias=None, host_template='host', force=False):
    """Adds a new host to Nagios. Returns true if operation is successful.

    Args:
     host_name -- Hostname of the host to be added
     address -- IP Address of the host (if None, it will be looked up in DNS)
     group_name -- Primary host/contactgroup for this host. (if none, use "default")
     templates -- List of template names to be added to this host
     use -- if this host inherits another host (i.e. "windows-server")
     host_template -- Use the specified host template instead of default host.cfg
     force -- Force operation. Overwrite config files needed.

    Examples:
    >>> addhost(host_name="localhost",group_name="database_servers") # doctest: +SKIP
    >>> addhost(host_name="okconfig.org", address="192.168.1.1") # doctest: +SKIP

    Returns:
     String message with result of addhost
    """
    if group_name is None or group_name is '': group_name = 'default'
    if templates is None: templates = []
    if alias is None: alias = host_name
    if address is None or address is '':
        try:
            address = socket.gethostbyname(host_name)
        except:
            raise OKConfigError("Could not resolve hostname '%s'" % host_name)
    if use is None:
        use = 'okc-default-host'
    okconfig_groups = get_groups()
    if len(okconfig_groups) == 0:
        addgroup(group_name='default',alias='OKconfig default group')
    arguments = {'PARENTHOST': use, 'GROUP': group_name, 'IPADDR': address, 'HOSTNAME': host_name, 'ALIAS': alias}
    destination_dir = "%s/hosts/%s/" % (destination_directory, group_name)
    destination_file = "%s/%s-host.cfg" % (destination_dir, host_name)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    if not force:
        if os.path.isfile(destination_file):
            raise OKConfigError("Destination file '%s' already exists." % destination_file)
        if group_name not in get_groups():
            #raise OKConfigError("Group %s does not exist" % group_name)
            addgroup(group_name)
        if host_name in get_hosts():
            filename = pynag.Model.Host.objects.get_by_shortname(host_name)._meta['filename']
            raise OKConfigError("Host named '%s' already exists in %s" % (host_name, filename))
    # Do sanity checking of all templates before we add anything
    all_templates = list(get_templates().keys())
    if host_template not in all_templates:
        raise OKConfigError("Host Template %s not found" % host_template)
    for i in templates:
        if i not in all_templates:
            raise OKConfigError("Template %s not found" % i)
    result = _apply_template(host_template, destination_file, **arguments)
    _git_commit(filelist=result, message='okconfig host %s added with address %s' % (host_name,address))
    for i in templates:
        result = result + addtemplate(host_name=host_name, template_name=i, group_name=group_name,force=force)
    return result
def addtemplate(host_name, template_name, group_name=None,force=False):
    """Adds a new template to existing host in Nagios.

    Args:
     host_name -- Hostname to add template to (i.e. "host.example.com")
     template_name -- Name of the template to be added (i.e. "mysql")
     force -- Force operation, overwrites configuration if it already exists

    Examples:
     addtemplate(host_name="host.example.com", template="mysql")

    Returns:
     True if operation is succesful.
    """
    try:
        host = pynag.Model.Host.objects.get_by_shortname(host_name)
    except (ValueError, KeyError):
        raise OKConfigError("Host '%s' was not found" % host_name)
    hostfile = host.get_filename()

    # If no group name is specified, try host.contact_groups
    if group_name is None: group_name = host.contact_groups
    if group_name is None: group_name = "default"

    if hostfile is None:
        raise OKConfigError("Host '%s' was not found" % host_name)
    if template_name not in list(get_templates().keys()):
        raise OKConfigError("Template '%s' was not found" % template_name)
    hostdir = os.path.dirname(hostfile)
    # Check if host has the required "default service"
    helper_functions.add_defaultservice_to_host(host_name)

    # Lets do some templating
    newfile = "%s/%s-%s.cfg" % (hostdir, host_name,template_name)
    if not force:
        # 'Do some basic sanity checking'
        if os.path.exists(newfile):
            raise OKConfigError("Destination file '%s' already exists." % newfile)

    result = _apply_template(template_name,newfile, HOSTNAME=host_name, GROUP=group_name)
    _git_commit(filelist=result, message='okconfig template %s added to host %s' % (template_name, host_name))
    return result

def addgroup(group_name, alias=None, force=False):
    """Adds a new hostgroup/contactgroup/servicegroup combo to Nagios.

    Args:
     group_name -- Name of the group to be added (i.e. "db-servers")
     alias -- Group alias (i.e. "Database Servers")
     force -- Force operation, overwrites configuration if it already exists

    Examples:
     addgroup(group_name="db-servers", alias="Database Servers")

    Returns:
     True if operation was successful
    """
    if alias is None: alias=group_name
    destination_dir = "%s/groups" % destination_directory
    destination_file = "%s/%s.cfg" % (destination_dir, group_name)
    if not force:
        # 'Do some sanity checking'
        if os.path.exists(destination_file):
            raise OKConfigError("Destination file '%s' already exists" % destination_file)
        groups = helper_functions.group_exists(group_name)
        if groups != False:
            raise OKConfigError("We already have groups with name = %s" % group_name)

    result = _apply_template(template_name="group",destination_file=destination_file, GROUP=group_name, ALIAS=alias)
    _git_commit(filelist=result, message="okconfig group %s added" % group_name)
    return result
def addcontact(contact_name, alias=None, force=False, group_name="default", email=None, use='generic-contact'):
    """Adds a new contact to Nagios.

    Args:
     contact_name -- Name of the contact to be added (i.e. "user@example.com")
     alias -- Contact alias (i.e. "Full Name")
     force -- Force operation, overwrites configuration if it already exists

    Examples:
     addcontact(contact_name="user@example.com", contact_groups="default", email="user@example.com")

    Returns:
     True if operation was successful
    """
    if group_name is None or group_name is '': group_name = 'default'
    # Check if contact already exists
    try:
        contact = pynag.Model.Contact.objects.get_by_shortname(contact_name)
        if not force:
            raise OKConfigError("contact %s already exists in file %s" % (contact_name, contact.get_filename()))
    except (KeyError, ValueError):
        contact = pynag.Model.Contact()
    contact['contact_name'] = contact_name
    if alias is not None: contact['alias'] = alias
    if use is not None: contact['use'] = use
    if email is not None: contact['email'] = email
    if group_name is not None: contact['contactgroups'] = group_name
    result = contact.save()
    filename = contact.get_filename()
    if result is False:
        raise OKConfigError("Failed to save contact to %s" % filename)
    return [filename]
def addservice(inherit_settings_from, host_name, service_description=None, group=None, check_command=None,force=False):
    """Adds a new service to Nagios.

    Args:
     inherit_settings_from -- Name of another service to inherit from (i.e. 'generic-service')
     service_description -- Description of the service as it will appear in nagios (i.e. "Disk Usage")
     host_name -- Host that this service check belongs to
     force -- Force operation, overwrites configuration if it already exists

    Examples:
     addservice(host_name="localhost, inherit_settings_from="okc-check_ping")

    Returns:
     True if operation was successful
    """

    # Check if host exists:
    tmp = pynag.Model.Host.objects.filter(host_name=host_name)
    if len(tmp) != 1:
        raise OKConfigError("Cannot find host named '%s'." % host_name)
    host = tmp[0]

    # Find a proper filename to save to
    dirname = os.path.dirname( host.get_filename() )
    filename = '%s/%s-custom.cfg' % (dirname, host_name)

    # Check if parent exists
    tmp = pynag.Model.Service.objects.filter(name=inherit_settings_from)
    if len(tmp) != 1:
        raise OKConfigError("cannot find service '%s' to inherit settings from" % inherit_settings_from)
    parent_service = tmp[0]

    if service_description is None:
        if parent_service.service_description is None:
            raise OKConfigError("service_description not defined and parent '%s' does not have any." % inherit_settings_from)
        service_description = parent_service.service_description
    tmp = pynag.Model.Service.objects.filter(host_name=host_name,service_description=service_description)
    if len(tmp) is 0: # Service not found. This is indeed a new service
        service = pynag.Model.Service()
        service._meta['filename'] = filename
    elif len(tmp) is 1: # There is another service defined just like this one
        service = tmp[0]
        if not force:
            filename = service.get_filename()
            raise OKConfigError("service is already defined in file %s. Will not add again." % filename)
    else: # Multiple services defined
        files = []
        for i in tmp:
            files.append(i.get_filename())
        raise OKConfigError("%s services already defined with same host_name/service_description. Will not add any more: %s " % (len(tmp), "; ".join(files)))

    service['host_name'] = host_name
    if service_description is not None:
        service['service_description'] = service_description
    if group is not None:
        service['contact_groups'] = group
    if check_command is not None:
        service['check_command'] = check_command
    result = service.save()
    if result is False:
        raise OKConfigError("Failed to save service to file" % service.get_filename())
    else:
        return [service.get_filename()]

def findhost(host_name):
    """Returns the filename which defines a specied host. Returns None on failure.

    Args:
     host_name -- Name of the host to find

    Examples:
    >>> print findhost("host.example.com") # doctest: +SKIP
    "/etc/okconfig/hosts/default/host.example.com-host.cfg"
    """
    try:
        my_host = pynag.Model.Host.objects.get_by_shortname(host_name)
        filename = my_host['meta']['filename']
        return filename
    except (ValueError, KeyError):
        return None

def removehost(host_name, recursive=True):
    """ Removes a specified host. And possibly all services for that host.

    Args:
        host_name -- Name of the host to remove
        recursive -- If true: Also delete all services that belong to this host.
    Examples:
    >>> removehost('host.example.com', recursive=True) # doctest: +SKIP
    """
    my_host = pynag.Model.Host.objects.get_by_shortname(host_name)
    my_host.delete(recursive=recursive)
    return True

def get_templates():
    """ Returns a list of available templates """
    result = {}
    if not os.path.isdir(examples_directory):
        raise OKConfigError("Examples directory does not exist: %s" % examples_directory)
    filelist = os.listdir(examples_directory)
    if os.path.isdir(examples_directory_local):
        for i in os.listdir(examples_directory_local):
            if i not in filelist:
                filelist.append(i)
    for file in filelist:
        if os.path.isfile(examples_directory + "/" + file): filename = examples_directory + "/" + file
        if os.path.isfile(examples_directory_local + "/" + file): filename = examples_directory_local + "/" + file
        if file.endswith('.cfg-example'):
            template_name = file[:-12]
            template_parents = []
            template_friendly_name = ''
            result[template_name] = {'parents':template_parents, 'filename':filename, 'name':template_friendly_name}
    return result

def get_hosts():
    """ Returns a list of available hosts """
    result = []
    hosts = pynag.Model.Host.objects.all
    for host in hosts:
        if host.get_shortname() not in result and host.get_shortname() is not None:
            result.append(host.get_shortname())
    return result

def get_groups():
    """ Returns a list of available groups """
    result = []
    group_directory = "%s/groups" % destination_directory
    # If group_directory does not exist, we dont have any groups
    if not os.path.isdir(group_directory):
        return result
    filelist = os.listdir(group_directory)
    for file in filelist:
        if os.path.isfile(group_directory + "/" + file) and file.endswith('.cfg'):
            name = file[:-4]
            result.append(name)
    result.sort()
    return result

def install_nsclient(remote_host, domain, username, password):
    """ Logs into remote (windows) host and installs NSClient.

    Args:
     remote_host -- Hostname/IPAddress of remote host
     username -- Name of a user with administrative privileges on the remote host
     password -- Password to use
     domain -- Windows Domain

    Returns:
     True if operation was successful. Otherwise False
    """
    if not network_scan.check_tcp(remote_host, 445, timeout=5):
        raise OKConfigError('Cannot reach remote_host on port 445, aborting...')

    result = pynag.Utils.runCommand("%s/install_nsclient.sh '%s' --domain '%s' --user '%s' --password '%s'" % (config.nsclient_installfiles,remote_host,domain,username,password))
    return result

def check_agent(host_name):
    """ Checks a remote host if it has a valid okconfig client configuration

    Args:
        host_name -- hostname (or ip address of remote host)
    Returns:
        True/False, [ "List","of","messages" ]
    """
    raise NotImplementedError()

def install_okagent(remote_host,username,password=None, domain=None, install_method=None):
    ''' Installs an okagent to remote host using either winexe or ssh method

    Args:
     remote_host    -- Hostname/IPAddress of remote host
     username       -- Username to use
     password       -- Password to use. If None, try to use ssh keys
     install_method -- Use either "winexe" or "ssh". Leave empty for autodetect.
    Returns:
     exit_status,stdout,stderr
    '''
    if not install_method or install_method == '':
        if network_scan.check_tcp(remote_host, 22, timeout=5):
            install_method = 'ssh'
        elif network_scan.check_tcp(remote_host, 445, timeout=5):
            install_method = 'winexe'

    if install_method == 'ssh':
        return install_nrpe(remote_host=remote_host,username=username, password=password)
    elif install_method == 'winexe':
        return install_nsclient(remote_host=remote_host,username=username, password=password, domain=domain)
    raise OKConfigError("Cannot connect to %s on port 22 or 445. No install method available" % (remote_host))

def install_nrpe(remote_host, username, password=None):
    """ Logs into remote (unix) host and install nrpe-client.

    Args:
     remote_host -- Hostname/IPAddress of remote host
     username -- Username to use
     password -- Password to use. If None, try to use ssh keys

    Returns:
     True if operation was successful.
    """
    if not paramiko:
        raise OKConfigError('You need to install python module: paramiko')
    if not network_scan.check_tcp(remote_host, 22, timeout=5):
        raise OKConfigError('Cannot reach remote_host on port 22, aborting...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    ssh.connect(remote_host, username=username, password=password)


    # Try a test command on the remote server to see if we are connected
    test_command = 'echo -e connection test'
    chan = ssh.get_transport().open_session()
    chan.exec_command( test_command )
    exit_status = chan.recv_exit_status()
    stdout = chan.recv(-1).strip()
    stderr = chan.recv_stderr(-1).strip()
    if exit_status != 0:
        ssh.close()
        raise OKConfigError('Exit code %s when trying to run test command\noutput: %s\nstderr: %s' % (chan.exit_status, stdout,stderr) )

    # Uploading install script to remote server
    sftp = ssh.open_sftp()
    sftp.put(config.install_nrpe_script, 'install_nrpe.sh')

    # Executing remote script
    # We need to do some hoola-hoops to get the exit code
    chan = ssh.get_transport().open_session()
    chan.exec_command('bash install_nrpe.sh')
    exit_status = chan.recv_exit_status()
    stdout = chan.recv(-1).strip()
    stderr = chan.recv_stderr(-1).strip()

    return exit_status,stdout,stderr

def _apply_template(template_name,destination_file, **kwargs):
    """ Applies okconfig template to filename, doing replacements from kwargs in the meantime

    Arguments:
        template_name - name of the template to use
        destination_file - full path to file to be written to
        kwargs key/value pair of string to search and replacement to make

    Example:
        _apply_template('host','/etc/nagios/okconfig/hosts/newhost.cfg', HOSTNAME='newhost',ADDRESS='0.0.0.0',GROUP='default')
    Returns:
        List of filenames that have been written to
    """
    all_examples = get_templates()
    if template_name not in all_examples:
        raise OKConfigError('Template %s cannot be found' % template_name)
    sourcefile = all_examples[template_name]['filename']

    # Clean // from destination file
    destination_file = destination_file.replace('//','/')

    if not os.path.isfile(sourcefile):
        raise OKConfigError('Template %s cannot be found' % template_name)

    dirname = os.path.dirname(destination_file)
    if not os.path.exists(dirname): os.makedirs(dirname)

    fd = open(sourcefile).read()
    for old_string,new_string in list(kwargs.items()):
        fd = fd.replace(old_string,new_string)
    open(destination_file,'w').write( fd )
    return [destination_file]

def _git_commit(filelist, message):
    """ If config.git_commit_changes is enabled, then commit "filelist" to the repository using message """
    if config.git_commit_changes != '1':
        return
    if 'git' not in globals():
        from pynag.Utils import GitRepo
        git = GitRepo(directory=os.path.dirname(config.nagios_config), auto_init=False, author_name="okconfig")
    else:
        git = globals()['git']
    git.commit(message=message, filelist=filelist)
class OKConfigError(Exception):
    pass

#all_templates = get_templates()
if __name__ == '__main__':
    pass
