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


"""
TEMPLATE_VERSION HISTORY

# Version 2.5 (2013-06-28)
    * okc-check_http has new service macro: __ON_REDIRECT
# Version 2.4 (2013-05-13)
    * Removed the following hardcoded groups from templates:
    * hostgroup cisco-hostgroup
    * servicegroup proliant-services
    * contactgroup proliant-contacts
    * servicegroup eva-services
    * contactgroup eva-contacts
    * servicegroup windows-services
    * servicegroup linux-services
    * servicegroup mssql-services
# Version 2.3 (2013-04-29)
    * okc-emc-check_portstate now enforces username and password
    * okc-check_http now has support for virtualhosts and ports
# Version 2.2 (2012-09-26)
    * Brocade templates reworked. _SNMP_COMMUNITY macro renamed to __SNMP_COMMUNITY

# Version 2.1 (2012-05-30)
    * All check_commands in templates directory have been given an okc- prefix
    * Deprecated host templates have been removed
    * default-host changed to okc-default-host
    * hostgroups removed

# Version 2 (2011-07-01):
    * All service names have been given an okc- prefix

# Version 1.1 (2011-07-01)
    * All "default service" created turned out to be registered

# Version 1 (2011-04-01):
    * templates now require a service called "$HOSTDESCR$", okc tools handle this automatically for new templates
    * Requires okconfig tools version 1
# Version 0:
    * Initial Release
"""


from __future__ import absolute_import
from __future__ import print_function
from pynag import Model
import okconfig

    
def get_template_version():
    """ Get the version number of the template directory """
    try:
        file = open("%s/metadata" % okconfig.template_directory)
        for line in file.readlines():
            line = line.split()
            if len(line) != 2: continue
            if line[0] == 'TEMPLATES_VERSION':
                return float(line[1])
        return 0
    except Exception:
        return 0



def upgrade_to_version_1_1():
    """ Hosts created with older addhost, might have some registered template services """
    print("Upgrading to config version 1.1 ...", end=' ')
    all_hosts = okconfig.get_hosts()
    my_services = Model.Service.objects.filter(register="1",name__contains='')
    for service in my_services:
        if service.name in all_hosts and not service['service_description']:
            service['register'] = 0
            print("Default service for %s updated" % service.name)
            service.save()
    print("ok")
def upgrade_to_version_2():
    """ Upgrades all nagios configuration file according to new okconfig templates
    
    Biggest change here is that all template services have been given a okc- prefix
    
    We have to find all services that have invalid parents.
    """
    print("Upgrading to config version 2.0 ...", end=' ')
    all_templates = Model.Service.objects.filter(name__contains='')
    all_templates = [x.name for x in all_templates]
    my_services = Model.Service.objects.filter(use__contains="")
    for service in my_services:
        old_use = service.use.split(',')
        new_use = []
        for i in old_use:
            okc_name = 'okc-%s' % i
            if not i in all_templates and okc_name in all_templates:
                # parent does not exist, but okc-parent does
                i = okc_name
            new_use.append( i )
        #new_use = ','.join(new_use)
        if old_use != new_use:
            service.use = ','.join(new_use)
            print(".. %s updated" % new_use)
            service.save()
    print("ok")
def upgrade_to_version_2_1():
    """ Upgrades all nagios configuration file according to new okconfig templates
    
    Biggest change here is that all template commands have been given a okc- prefix
    
    We have to find all services that have invalid check_command.
    """
    print("Upgrading to config version 2.1 ...", end=' ')
    all_commands = Model.Command.objects.all
    all_commands = [x.command_name for x in all_commands]
    my_services = Model.Service.objects.all
    for i in my_services:
        # Only work on services that actually define check_command
        if 'check_command' not in i._defined_attributes: continue
        
        # We only need the actual command, not any parameters
        check_command = i.check_command.split('!',1)[0]
        
        # If check_command is valid, then there is nothing to do
        if check_command in all_commands: continue
        
        # if command is missing, it might have been renamed by okconfig:
        if "okc-%s"%check_command in all_commands:
            i.check_command = "okc-%s"%i.check_command
            i.save()
            print("%s renamed to okc-%s"%(check_command,check_command))

    # Update notification commands on all contacts
    for i in Model.Contact.objects.all:
        current = i.service_notification_commands
        if current not in all_commands and "okc-%s"%current in all_commands:
            i.service_notification_commands = "okc-%s"%current
            i.save()
        current = i.host_notification_commands
        if current not in all_commands and "okc-%s"%current in all_commands:
            i.host_notification_commands = "okc-%s"%current
            i.save()
    # Check for hosts
    deprecated_hostnames = ('generic-server-dev', 'generic-server-prod', 'generic-server-crit', 'generic-server', 'default-host')
    new_hostname = "okc-default-host"
    
    all_templates = Model.Host.objects.filter(name__contains='')
    all_templates = [x.name for x in all_templates]
    my_hosts = Model.Host.objects.filter(use__contains="")
    for host in my_hosts:
        old_use = host.use.split(',')
        new_use = []
        for i in old_use:
            okc_name = 'okc-%s' % i
            if not i in all_templates and okc_name in all_templates:
                # parent does not exist, but okc-parent does
                i = okc_name
            elif not i in all_templates and i in deprecated_hostnames:
                i = new_hostname
            new_use.append( i )
        #new_use = ','.join(new_use)
        if old_use != new_use:
            host.use = ','.join(new_use)
            print(".. %s updated" % old_use)
            host.save() 
    print("ok")
def upgrade_to_version_2_2():
    """ Upgrades all nagios configuration file according to new okconfig templates

    Biggest Change here is that brocade templates previously had macro _SNMP_COMMUNITY which has been
    renamed to __SNMP_COMMUNITY
    """
    print("Upgrading to config version 2.2 ...", end=' ')
    my_services = Model.Service.objects.filter(use__contains='okc-brocade')
    for service in my_services:
        if service.host_name is None:
            continue
        if service['_SNMP_COMMUNITY'] in (None,'public'):
            continue
        if not service['__SNMP_COMMUNITY'] == 'public':
            continue
        print("..", service.get_description(), "renamed _SNMP_COMMUNITY %s to __SNMP_COMMUNITY" % (service['_SNMP_COMMUNITY']))
    print("ok")

def upgrade_to_version_2_3():
    """ Upgrade to version 2.3
     okc-emc_check_port_state now has a username and password field implied
    """
    print("Upgrading to config version 2.3 ...", end=' ')
    my_services = Model.Service.objects.filter(check_command="okc-emc-check_portstate", __USERNAME=None, register=1)
    for i in my_services:
        if i.get('__USERNAME') is None:
            i['__USERNAME'] = 'nagios'
        if i.get('__PASSWORD') is None:
            i['__PASSWORD'] = 'not set'
        i.save()
        print("Updated: ", i.get_shortname())

    # Add missing macros to okc-check_http
    my_services = Model.Service.objects.filter(check_command="okc-check_http", __VIRTUAL_HOST=None, register=1)
    for i in my_services:
        if i.get('__VIRTUAL_HOST') is None:
            i['__VIRTUAL_HOST'] = i.get('host_name')
        if i.get('__PORT') is None:
            i['__PORT'] = "80"
        i.save()
        print("Updated: ", i.get_shortname())

    my_services = Model.Service.objects.filter(check_command="okc-check_https", __VIRTUAL_HOST=None, register=1)
    for i in my_services:
        if i.get('__VIRTUAL_HOST') is None:
            i['__VIRTUAL_HOST'] = i.get('host_name')
        if i.get('__PORT') is None:
            i['__PORT'] = "443"
        i.save()
        print("Updated: ", i.get_shortname())

    my_services = Model.Service.objects.filter(check_command="okc-check_https_certificate", __PORT=None, register=1)
    for i in my_services:
        if i.get('__PORT') is None:
            i['__PORT'] = "443"
        i.save()
        print("Updated: ", i.get_shortname())
    print("ok")

def upgrade_to_version_2_4():
    """ Upgrade to version 2.4
    We will adapt to the following removals:
    * hostgroup cisco-hostgroup
    * servicegroup proliant-services
    * contactgroup proliant-contacts
    * servicegroup eva-services
    * contactgroup eva-contacts
    * servicegroup windows-services
    * servicegroup linux-services
    * servicegroup mssql-services
    """
    print("Upgrading to config version 2.4 ...", end=' ')
    dest_file = okconfig.config.destination_directory + "/backwards-compatibility.cfg"
    hostgroups = ['cisco-hostgroup']
    servicegroups = ['proliant-services', 'eva-services', 'windows-services', 'linux-services', 'mssql-services']
    contactgroups = ['proliant-contacts', 'eva-contacts']
    for i in hostgroups:
        hg = Model.Hostgroup.objects.filter(hostgroup_name=i)
        hg_hosts = Model.Host.objects.filter(host_groups__has_field=i)
        if hg_hosts and not hg:
            h = Model.Hostgroup()
            h['hostgroup_name'] = i
            h['alias'] = i
            h.set_filename(dest_file)
            h.save()
            print("Created hostgroup", i)
    for i in servicegroups:
        sg = Model.Servicegroup.objects.filter(servicegroup_name=i)
        sg_services = Model.Service.objects.filter(service_groups__has_field=i)
        if sg_services and not sg:
            s = Model.Servicegroup()
            s['servicegroup_name'] = i
            s['alias'] = i
            s.set_filename(dest_file)
            s.save()
            print("Created servicegroup", i)
    for i in contactgroups:
        cg = Model.Contactgroup.objects.filter(contactgroup_name=i)
        cg_contacts = Model.Contact.objects.filter(contactgroups__has_field=i)
        cg_hosts = Model.Host.objects.filter(contact_groups__has_field=i)
        cg_services = Model.Host.objects.filter(contact_groups__has_field=i)
        if not cg and (cg_contacts or cg_hosts or cg_services):
            c = Model.Contactgroup()
            c['contactgroup_name'] = i
            c['alias'] = i
            c.set_filename(dest_file)
            c.save()
            print("Created contactgroup", i)
    print("ok")

def upgrade_to_version_2_5():
    """ Upgrade to version 2.5

    We will adapt to the following changes:
    * okc-check_http* has a new service variable __ON_REDIRECT

    """
    print("Upgrading to config version 2.5 ...", end=' ')
    services = Model.Service.objects.filter(check_command__startswith='okc-check_http', __ON_REDIRECT__exists=False)
    for i in services:
        i['__ON_REDIRECT'] = "follow"
        i.save()
    print("ok")




def rename_oktemplate_services():
    """ To change config version to 2.0 This is a one-off action. Not part of any upgrade """
    all_obj = Model.Service.objects.filter(name__contains='',filename__startswith=okconfig.template_directory)
    for i in all_obj:
        if i.name.startswith('okc-'): continue
        i['name'] = "okc-%s" % i.name
        i.save()    



def upgrade_okconfig():
    """Upgrades nagios configuration to match the level of current oktemplates format"""
    template_version = get_template_version()
    print("Upgrading to version %s" % template_version)
    if template_version >= 1:
        # "We dont need to do anything, the tools have been upgraded"
        pass
    if template_version >= 1.1:
        upgrade_to_version_1_1()
    if template_version >= 2:
        upgrade_to_version_2()
    if template_version >= 2.1:
        upgrade_to_version_2_1()
    if template_version >= 2.2:
        upgrade_to_version_2_2()
    if template_version >= 2.3:
        upgrade_to_version_2_3()
    if template_version >= 2.4:
        upgrade_to_version_2_4()
    if template_version >= 2.5:
        upgrade_to_version_2_5()

if __name__ == '__main__':
    upgrade_okconfig()
