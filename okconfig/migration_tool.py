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
    print "Upgrading to config version 1.1 ...",
    all_hosts = okconfig.get_hosts()
    my_services = Model.Service.objects.filter(register="1",name__contains='')
    for service in my_services:
        if service.name in all_hosts and not service['service_description']:
            service['register'] = 0
            print "Default service for %s updated" % service.name
            service.save()
    print "ok"
def upgrade_to_version_2():
    """ Upgrades all nagios configuration file according to new okconfig templates
    
    Biggest change here is that all template services have been given a okc- prefix
    
    We have to find all services that have invalid parents.
    """
    print "Upgrading to config version 2.0 ...",
    all_templates = Model.Service.objects.filter(name__contains='')
    all_templates = map(lambda x: x.name, all_templates)
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
            print ".. %s updated" % new_use
            service.save()
    print "ok"
def upgrade_to_version_2_1():
    """ Upgrades all nagios configuration file according to new okconfig templates
    
    Biggest change here is that all template commands have been given a okc- prefix
    
    We have to find all services that have invalid check_command.
    """
    print "Upgrading to config version 2.1 ...",
    all_commands = Model.Command.objects.all
    all_commands = map(lambda x: x.command_name, all_commands)
    my_services = Model.Service.objects.all
    for i in my_services:
        # Only work on services that actually define check_command
        if not i._defined_attributes.has_key('check_command'): continue
        
        # We only need the actual command, not any parameters
        check_command = i.check_command.split('!',1)[0]
        
        # If check_command is valid, then there is nothing to do
        if check_command in all_commands: continue
        
        # if command is missing, it might have been renamed by okconfig:
        if "okc-%s"%check_command in all_commands:
            i.check_command = "okc-%s"%i.check_command
            i.save()
            print "%s renamed to okc-%s"%(check_command,check_command)

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
    all_templates = map(lambda x: x.name, all_templates)
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
            print ".. %s updated" % old_use
            host.save() 
    print "ok"
def upgrade_to_version_2_2():
    """ Upgrades all nagios configuration file according to new okconfig templates

    Biggest Change here is that brocade templates previously had macro _SNMP_COMMUNITY which has been
    renamed to __SNMP_COMMUNITY
    """
    print "Upgrading to config version 2.2 ...",
    my_services = Model.Service.objects.filter(use__contains='okc-brocade')
    for service in my_services:
        if service.host_name is None:
            continue
        if service['_SNMP_COMMUNITY'] in (None,'public'):
            continue
        if not service['__SNMP_COMMUNITY'] == 'public':
            continue
        print "..", service.get_description(), "renamed _SNMP_COMMUNITY %s to __SNMP_COMMUNITY" % (service['_SNMP_COMMUNITY'])
    print "ok"


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
    print "Upgrading to version %s" % template_version
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

if __name__ == '__main__':
    upgrade_okconfig()
