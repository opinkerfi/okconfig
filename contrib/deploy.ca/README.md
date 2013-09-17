Deployment scripts for Jan Stembera
===================================

This directory contains scripts and utilities made for Jan Stembera. They are wrappers around okconfig install agent
and network scan features, modified so that output is json and input meets Jan's needs.

Files in this directory
=======================

* install_nagios_agent  - Installs NRPE and the typical okconfig plugins on a remote RHEL/Centos 6 server
* network_scan          - Ping scans a network, and returns in json format discovered hosts


Prerequisites
=============

The nagios server will need the following packages installed:

* okconfig
* pynag
* nagios-plugins-fping


Additionally the okconfig rpm has the following dependencies which should be automatically installed
via yum:
```
Requires: pynag python-paramiko winexe
Requires: nagios nagios-plugins-nrpe  nagios-plugins-ping nagios-plugins-ssh
Requires: nagios-okplugin-apc nagios-okplugin-brocade nagios-okplugin-mailblacklist
Requires: nagios-okplugin-check_disks nagios-okplugin-check_time nagios-plugins-fping
```

Deploying a nagios agent to a remote server
===========================================
To deploy the NRPE agent to a remote server, the nagios server will need ssh root access to the remote server. The
agent supports both logging in via ssh key or via password authentication.

After the agent has been installed, the access needed from the nagios server varies, but typically the nagios server needs
at the very least access on port 5666 so it can talk with the NRPE agent.

When the deploy script runs it will log into the remote server and execute a custom shell script designed to install NRPE
agent and configure it so it is compatible with the default okconfig linux package. The shell script can be reviewed here:
https://github.com/opinkerfi/okconfig/blob/master/usr/share/okconfig/client/linux/install_okagent.sh

install_nagios_agent usage
==========================

Here is an example usage of the install_nagios_agent script

```
bash # ./install_nagios_agent x01=root x02=root_password x03=xxx x04=localhost
{
  'success': true,
  'msg': 'Client successfully installed'
}
```

In the case of a failure it will return:
```
{
  'success': false,
  'msg': 'An error message saying that something went wrong'
}
```

network_scan usage
==================

...


