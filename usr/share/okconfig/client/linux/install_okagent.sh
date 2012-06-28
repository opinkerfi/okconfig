#!/bin/bash

INSTALL_DIR=`dirname $0`
NAGIOS_SERVER=$1


if [ -z $NAGIOS_SERVER ] ; then
	NAGIOS_SERVER=`echo $SSH_CLIENT | awk '{ print $1 }'`
	echo "IP Address of Nagios server not specified. Using $NAGIOS_SERVER"
fi


echo 'Running rpm --force -Uhv http://opensource.is/repo/ok-release-10-1.el5.centos.noarch.rpm'
rpm -Uhv --force http://opensource.is/repo/ok-release-10-1.el5.centos.noarch.rpm
if [ 0 -ne $? ]; then
	echo "Failed to install ok-release yum repository" >2
	exit 1
fi
	
	
echo "Running: yum install -y nagios-okconfig-nrpe"
yum install -y nagios-okconfig-nrpe
if [ 0 -ne $? ]; then
	echo "Failed to yum install nagios-okconfig-nrpe package" >2
	exit 1
fi

echo "Cleaning up stock /etc/nagios/nrpe.cfg"
cat << EOF > /etc/nagios/nrpe.cfg
log_facility=daemon
pid_file=/var/run/nrpe/nrpe.pid
server_port=5666
nrpe_user=nrpe
nrpe_group=nrpe

# Replace this with actual ip address of your nagios server
allowed_hosts=IP_ADDRESS_OF_NAGIOS
 
dont_blame_nrpe=1
debug=0
command_timeout=60
connection_timeout=300
include_dir=/etc/nrpe.d/


command[check_users]=/usr/lib64/nagios/plugins/check_users -w 5 -c 10
command[check_hda1]=/usr/lib64/nagios/plugins/check_disk -w 20% -c 10% -p /dev/hda1
command[check_zombie_procs]=/usr/lib64/nagios/plugins/check_procs -w 5 -c 10 -s Z
EOF >



sed -i "s/IP_ADDRESS_OF_NAGIOS/$NAGIOS_SERVER/" /etc/nagios/nrpe.cfg

service nrpe start
chkconfig nrpe on

echo "Install Complete"
exit  0
