[![Build Status](https://travis-ci.org/opinkerfi/okconfig.png?branch=master)](https://travis-ci.org/opinkerfi/okconfig)
[![Coverage Status](https://coveralls.io/repos/opinkerfi/okconfig/badge.png?branch=master)](https://coveralls.io/r/opinkerfi/okconfig?branch=master)

About
=====

okconfig a robust template mechanism for Nagios configuration files. Providing
standardized set of configuration templates and select quality plugins 
to enterprise quality monitoring.



Getting Started
===============

Standard http checks on example.com:

    okconfig addhost --host example.com --template http

Also check ssl connection and ssl certificate:

    okconfig addtemplate --host example.com --template https

Create a new host and give them standard linux checks. Then install nrpe on it:

    okconfig addhost --host linuxhost.example.com --address 127.1.1.1 --template linux
    okconfig install --host linuxhost.example.com --ssh --user root --password my_password


Add mssql service checks to an existing host:

    okconfig addtemplate --host sqlserver.example.com --template mssql


Supported Platforms for nagios server
=====================================

The developers work hard to make sure templates, packages and plugins and
service checks work and don't break when okconfig is upgraded.

With over 60 plugins and 380 service templates there are limits to how many
platforms we can support. Currently we support running the nagios server on:

* RHEL 6.x / 7.x
* Centos 6.x / 7.x / 8.x

If anyone is willing to provide decent quality packages for debian or
other distros we are happy to build and host them.

Installing on rhel/centos
===============================

    rpm -Uvh http://download.fedoraproject.org/pub/epel/6/$HOSTTYPE/epel-release-6-8.noarch.rpm
    rpm -Uhv http://opensource.is/repo/ok-release-10-1.el6.noarch.rpm
    yum-config-manager --enable ok-testing
    
    yum install okconfig
    okconfig verify

Requirements
============
At the very least okconfig needs the following:

* python-2.6
* pynag-0.4.9
* python-paramiko (for deploying remote agents via ssh)
* winexe (for deploying remote agents to windows servers)

Installing from source
======================

If you want to play with the source or try it out on an unsupported platform. These 
instructions should get you started:

    cd /opt
    git clone https://github.com/opinkerfi/okconfig.git
    echo 'export PYTHONPATH=$PYTHONPATH:/opt/okconfig' > /etc/profile.d/okconfig.sh
    cp /opt/okconfig/etc/okconfig.conf /etc/okconfig.conf
    source /etc/profile
    
    ln -s /opt/okconfig/usr/share/okconfig /usr/share/
    ln -s /opt/okconfig/usr/bin/okconfig /usr/local/bin/
    
    # Remember to edit /etc/okconfig.conf and verify all paths apply to your system
    # Configure Nagios.cfg
    okconfig init
    
    # Test
    okconfig verify


Contact us
==========

* Github: For bug repors or feature requests: https://github.com/opinkerfi/okconfig
* Via irc: Developers are known to hang on #adagios and #pynag on freenode
