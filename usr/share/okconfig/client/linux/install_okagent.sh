#!/bin/bash

INSTALL_DIR=`dirname $0`
NAGIOS_SERVER=$1


if [ -z $NAGIOS_SERVER ] ; then
	NAGIOS_SERVER=`echo $SSH_CLIENT | awk '{ print $1 }'`
	echo "IP Address of Nagios server not specified. Using $NAGIOS_SERVER"
fi

grep -q "release 6" /etc/redhat-release 2>/dev/null && DISTRO=rhel6
grep -q "release 5" /etc/redhat-release 2>/dev/null && DISTRO=rhel5
test -f /etc/debian_version && DISTRO=debian


install_debian() {

# Install available packages
echo "Debian compatible distro... Installing debs"
apt-get install -y nagios-nrpe-server nagios-plugins
mkdir -p $NRPE_D

# For some versions of debian nrpe rundir is not created
#mkdir -p /var/run/$NAGIOS_USER
#chown $NAGIOS_USER /var/run/$NAGIOS_USER

# Throw in a check_procs script
cat << EOF > $PLUGINDIR/check_procs.sh
#!/bin/bash
LINE=\`$PLUGINDIR/check_procs \$*\`
RC=$?
COUNT=\`echo \$LINE | awk '{print \$3}'\`
echo \$LINE \| procs=\$COUNT
exit \$RC
EOF

chmod a+x $PLUGINDIR/check_procs.sh


# Throw in check_cpu.sh
cd $PLUGINDIR
wget http://pall.sigurdsson.is/filez/check_cpu.sh
chmod a+rx check_cpu.sh

cat << EOF > $NRPE_D/check_cpu.cfg
command[check_cpu]=/usr/lib/nagios/plugins/check_cpu.sh
EOF




rm -rf $NRPE_D/config




clean_nrpe


cat << EOF > $NRPE_D/ok-bundle.cfg
# OK Nrpe configuration
# Try to be as flexible as possible, with as little dependencies as possible
command[get_disks]=/bin/df -k -x none -x tmpfs -x shmfs -x unknown -x iso9660
command[get_time]=/bin/date +%s
command[get_proc]=ps -Aw -o pid,ppid,user,start,state,pri,pcpu,time,pmem,rsz,vsz,cmd
command[get_netstat]=netstat -an
command[get_ifconfig]=/sbin/ifconfig
command[get_uptime]=uptime
command[get_selinux]=getenfore
command[get_lvm_vgs]=sudo /sbin/vgs --all -o all --nameprefixes --noheadings
command[get_lvm_lvs]=sudo /sbin/lvs --all -o all --nameprefixes --noheadings
command[get_lvm_pvs]=sudo /sbin/pvs --all -o all --nameprefixes --noheadings
command[get_rpms]=rpm -qa --queryformat 'PACKAGES="%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}" NAME="%{NAME}" INSTALLTIME="%{INSTALLTIME}" VERSION="%{VERSION}" RELEASE="%{RELEASE}" ARCH="%{ARCH}" VENDOR="%{VENDOR}" LICENSE="%{LICENSE}"\n'



# The following require dont_blame_nrpe to be on
# Please be careful what commands you add here
command[check_ntp_time]=$PLUGINDIR/check_ntp_time -H '\$ARG1\$' -w '\$ARG2\$' -c '\$ARG3\$' 
command[check_procs]=$PLUGINDIR/check_procs.sh -w '\$ARG1\$' -c '\$ARG2\$' -C '\$ARG3\$'
command[check_swap]=$PLUGINDIR/check_swap -w '\$ARG1\$' -c '\$ARG2\$' --allswaps
command[check_disk]=$PLUGINDIR/check_disk -w '\$ARG1\$' -c '\$ARG2\$' -p '\$ARG3\$'
command[check_load]=$PLUGINDIR/check_load -w '\$ARG1\$' -c '\$ARG2\$'
command[check_total_procs]=$PLUGINDIR/check_procs.sh -w '\$ARG1\$' -c '\$ARG2\$'

EOF


service nagios-nrpe-server restart
service nagios-nrpe-server reload

}


install_rhel() {

echo "RHEL compatible distro... Installing rpms"
echo $PLUGINDIR - $NRPE_D
exit
cat << EOF > /etc/yum.repos.d/ok.repo
[ok]
name=Opin Kerfi Public Repo - \$basearch
baseurl=http://opensource.is/repo/$DISTRO/\$basearch
failovermethod=priority
enabled=1
gpgcheck=0

[ok-testing]
name=Opin Kerfi Public Repo - Testing - \$basearch
baseurl=http://opensource.is/repo/testing/$DISTRO/\$basearch
failovermethod=priority
enabled=0
gpgcheck=0
EOF

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

clean_nrpe ;




service nrpe start
chkconfig nrpe on

echo "Install Complete"
exit  0
}

clean_nrpe() {
echo "Cleaning up stock /etc/nagios/nrpe.cfg"
cat << EOF > /etc/nagios/nrpe.cfg
log_facility=daemon
pid_file=/var/run/$NRPE_USER/nrpe.pid
server_port=5666
nrpe_user=nagios
nrpe_group=nagios

dont_blame_nrpe=1
debug=0
command_timeout=60
connection_timeout=300
include_dir=$NRPE_D


command[check_users]=$PLUGINDIR/check_users -w 5 -c 10
command[check_hda1]=$PLUGINDIR/check_disk -w 20% -c 10% -p /dev/hda1
command[check_zombie_procs]=$PLUGINDIR/check_procs -w 5 -c 10 -s Z
EOF

echo "allowed_hosts=$NAGIOS_SERVER"> $NRPE_D/allowed_hosts.cfg
}




if [ "$DISTRO" == "rhel6" ]; then
	PLUGINDIR=/usr/lib64/nagios/plugins/
	NRPE_USER=nrpe
	if [ $HOSTTYPE == "i386" ]; then
		PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
	fi	
	NRPE_D=/etc/nrpe.d/
	install_rhel;
elif [ "$DISTRO" == "rhel5" ]; then
	PLUGINDIR=/usr/lib64/nagios/plugins/
	NRPE_USER=nrpe
	if [ $HOSTTYPE == "i386" ]; then
		PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
	fi	
	NRPE_D=/etc/nrpe.d
	install_rhel;
elif [ "$DISTRO" == "debian" ]; then
	PLUGINDIR=/usr/lib/nagios/plugins/
	NRPE_D=/etc/nrpe.d
	NRPE_USER=nagios
	install_debian
else
	echo could not detect distribution. Exiting...
	exit 1
fi
