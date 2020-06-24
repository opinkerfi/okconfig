#!/bin/bash

INSTALL_DIR=`dirname $0`
NAGIOS_SERVER=$1


if [ -z $NAGIOS_SERVER ] ; then
	NAGIOS_SERVER=`echo $SSH_CLIENT | awk '{ print $1 }'`
	echo "IP Address of Nagios server not specified. Using $NAGIOS_SERVER"
fi

get_os_release() {
        # Run in a sub-shell so we do not overwrite any environment variables
        (
                . /etc/os-release
                echo ${ID}${VERSION_ID}
        )
}

fatal_error() {
	local message
	message="$1"

	echo "${message}" 1>&2
	exit 1
}

# Use /etc/os-release, see http://0pointer.de/blog/projects/os-release
if [ -f "/etc/os-release" ]; then
	DISTRO=$(get_os_release)
else
	grep -q "release 8" /etc/redhat-release 2>/dev/null && DISTRO=rhel8
	grep -q "release 7" /etc/redhat-release 2>/dev/null && DISTRO=rhel7
	grep -q "release 6" /etc/redhat-release 2>/dev/null && DISTRO=rhel6
	grep -q "release 5" /etc/redhat-release 2>/dev/null && DISTRO=rhel5
	grep -q "openSUSE 11" /etc/SuSE-release 2>/dev/null && DISTRO=opensuse
	test -f /etc/debian_version && DISTRO=debian
fi

install_debian() {

# Install available packages
echo "Debian compatible distro... Installing debs"
export DEBIAN_FRONTEND=noninteractive
apt-get install -y nagios-nrpe-server nagios-plugins bc
mkdir -p $NRPE_D

# For some versions of debian nrpe rundir is not created
#mkdir -p /var/run/$NAGIOS_USER
#chown $NAGIOS_USER /var/run/$NAGIOS_USER

install_check_procs;
install_check_cpu;

rm -rf $NRPE_D/config

clean_nrpe


configure_ok_bundle;

service nagios-nrpe-server restart
service nagios-nrpe-server reload

}

install_opensuse() {
	zypper install nagios-nrpe nagios-plugins

	clean_nrpe;
	install_check_procs;
	install_check_cpu;
	configure_ok_bundle;
	
	service nrpe restart
	chkconfig nrpe on

	echo "install complete"
	exit 0
}

install_rhel() {

        if [[ $DISTRO =~ centos[5678] ]]; then
                REPO=$(echo $DISTRO | sed 's/centos/rhel/g')
        elif [[ $DISTRO =~ rhel[5678] ]]; then
                REPO=$(echo $DISTRO | egrep -o "[a-z]+[0-9]") #not sure if OK repo broken or this broken
        else
                REPO=$DISTRO
        fi

	cat << EOF > /etc/yum.repos.d/ok.repo || fatal_error "Failed to install ok-release yum repository"
[ok]
name=Opin Kerfi Public Repo - \$basearch
baseurl=http://opensource.is/repo/$REPO/\$basearch
failovermethod=priority
enabled=1
gpgcheck=0

[ok-testing]
name=Opin Kerfi Public Repo - Testing - \$basearch
baseurl=http://opensource.is/repo/testing/$REPO/\$basearch
failovermethod=priority
enabled=0
gpgcheck=0
EOF

        echo "Installing epel repository"
        rpm -q epel-release || yum install -y epel-release || fatal_error "Failed to install EPEL yum repositories"
        
        echo "Running: yum install -y nagios-okconfig-nrpe"
        rpm -q nagios-okconfig-nrpe || yum install -y nagios-okconfig-nrpe || fatal_error "Failed to yum install nagios-okconfig-nrpe package"
        
        clean_nrpe ;
        
        if [[ $DISTRO = rhel7 || $DISTRO = centos7 || $DISTRO = centos8 || $DISTRO = rhel8 ]]; then
                systemctl start nrpe
                systemctl enable nrpe
        else
                service nrpe start
                chkconfig nrpe on
        fi
         
        echo "Install Complete"
        exit  0
}

clean_nrpe() {

mkdir -p $NRPE_D
echo "Cleaning up stock /etc/nagios/nrpe.cfg"
cp -fb /etc/nagios/nrpe.cfg /etc/nagios/nrpe.cfg~
cat << EOF > /etc/nagios/nrpe.cfg
log_facility=daemon
pid_file=/var/run/$NRPE_USER/nrpe.pid
server_port=5666
nrpe_user=${NRPE_USER}
nrpe_group=${NRPE_USER}

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


install_check_procs() {

# Throw in a check_procs script
cat << EOF > $PLUGINDIR/check_procs.sh
#!/bin/bash
LINE=\`$PLUGINDIR/check_procs \$*\`
RC=\$?
COUNT=\`echo \$LINE | awk '{print \$3}'\`
echo \$LINE \| procs=\$COUNT
exit \$RC
EOF

chmod a+x $PLUGINDIR/check_procs.sh


}

install_check_cpu() {
# Throw in check_cpu.sh
cat << 'EOF' > $PLUGINDIR/check_cpu.sh
#!/bin/sh

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

PROGNAME=`basename $0`
VERSION="Version 1.0,"
AUTHOR="2009, Mike Adolphs (http://www.matejunkie.com/)"

ST_OK=0
ST_WR=1
ST_CR=2
ST_UK=3

interval=1

print_version() {
    echo "$VERSION $AUTHOR"
}

print_help() {
    print_version $PROGNAME $VERSION
    echo ""
    echo "$PROGNAME is a Nagios plugin to monitor CPU utilization. It makes"
	echo "use of /proc/stat and calculates it through Jiffies rather than"
	echo "using another frontend tool like iostat or top."
	echo "When using optional warning/critical thresholds all values except"
	echo "idle are aggregated and compared to the thresholds. There's"
	echo "currently no support for warning/critical thresholds for specific"
	echo "usage parameters."
    echo ""
    echo "$PROGNAME [-i/--interval] [-w/--warning] [-c/--critical]"
    echo ""
    echo "Options:"
	echo "  --interval|-i)"
	echo "    Defines the pause between the two times /proc/stat is being"
	echo "    parsed. Higher values could lead to more accurate result."
	echo "    Default is: 1 second"
    echo "  --warning|-w)"
    echo "    Sets a warning level for CPU user. Default is: off"
    echo "  --critical|-c)"
    echo "    Sets a critical level for CPU user. Default is: off"
    exit $ST_UK
}

while test -n "$1"; do
    case "$1" in
        --help|-h)
            print_help
            exit $ST_UK
            ;;
        --version|-v)
            print_version $PROGNAME $VERSION
            exit $ST_UK
            ;;
        --interval|-i)
            interval=$2
            shift
            ;;
        --warning|-w)
            warn=$2
            shift
            ;;
        --critical|-c)
            crit=$2
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            print_help
            exit $ST_UK
            ;;
    esac
    shift
done

val_wcdiff() {
    if [ ${warn} -gt ${crit} ]
    then
        wcdiff=1
    fi
}

get_cpuvals() {
	tmp1_cpu_user=`grep -m1 '^cpu' /proc/stat|awk '{print $2}'`
	tmp1_cpu_nice=`grep -m1 '^cpu' /proc/stat|awk '{print $3}'`
	tmp1_cpu_sys=`grep -m1 '^cpu' /proc/stat|awk '{print $4}'`
	tmp1_cpu_idle=`grep -m1 '^cpu' /proc/stat|awk '{print $5}'`
	tmp1_cpu_iowait=`grep -m1 '^cpu' /proc/stat|awk '{print $6}'`
	tmp1_cpu_irq=`grep -m1 '^cpu' /proc/stat|awk '{print $7}'`
	tmp1_cpu_softirq=`grep -m1 '^cpu' /proc/stat|awk '{print $8}'`
	tmp1_cpu_total=`expr $tmp1_cpu_user + $tmp1_cpu_nice + $tmp1_cpu_sys + \
$tmp1_cpu_idle + $tmp1_cpu_iowait + $tmp1_cpu_irq + $tmp1_cpu_softirq`

	sleep $interval

	tmp2_cpu_user=`grep -m1 '^cpu' /proc/stat|awk '{print $2}'`
	tmp2_cpu_nice=`grep -m1 '^cpu' /proc/stat|awk '{print $3}'`
	tmp2_cpu_sys=`grep -m1 '^cpu' /proc/stat|awk '{print $4}'`
	tmp2_cpu_idle=`grep -m1 '^cpu' /proc/stat|awk '{print $5}'`
	tmp2_cpu_iowait=`grep -m1 '^cpu' /proc/stat|awk '{print $6}'`
	tmp2_cpu_irq=`grep -m1 '^cpu' /proc/stat|awk '{print $7}'`
	tmp2_cpu_softirq=`grep -m1 '^cpu' /proc/stat|awk '{print $8}'`
	tmp2_cpu_total=`expr $tmp2_cpu_user + $tmp2_cpu_nice + $tmp2_cpu_sys + \
$tmp2_cpu_idle + $tmp2_cpu_iowait + $tmp2_cpu_irq + $tmp2_cpu_softirq`

	diff_cpu_user=`echo "${tmp2_cpu_user} - ${tmp1_cpu_user}" | bc -l`
	diff_cpu_nice=`echo "${tmp2_cpu_nice} - ${tmp1_cpu_nice}" | bc -l`
	diff_cpu_sys=`echo "${tmp2_cpu_sys} - ${tmp1_cpu_sys}" | bc -l`
	diff_cpu_idle=`echo "${tmp2_cpu_idle} - ${tmp1_cpu_idle}" | bc -l`
	diff_cpu_iowait=`echo "${tmp2_cpu_iowait} - ${tmp1_cpu_iowait}" | bc -l`
	diff_cpu_irq=`echo "${tmp2_cpu_irq} - ${tmp1_cpu_irq}" | bc -l`
	diff_cpu_softirq=`echo "${tmp2_cpu_softirq} - ${tmp1_cpu_softirq}" \
| bc -l`
	diff_cpu_total=`echo "${tmp2_cpu_total} - ${tmp1_cpu_total}" | bc -l`

	cpu_user=`echo "scale=2; (1000*${diff_cpu_user}/${diff_cpu_total}+5)/10" \
| bc -l | sed 's/^\./0./'`
	cpu_nice=`echo "scale=2; (1000*${diff_cpu_nice}/${diff_cpu_total}+5)/10" \
| bc -l | sed 's/^\./0./'`
	cpu_sys=`echo "scale=2; (1000*${diff_cpu_sys}/${diff_cpu_total}+5)/10" \
| bc -l | sed 's/^\./0./'`
	cpu_idle=`echo "scale=2; (1000*${diff_cpu_idle}/${diff_cpu_total}+5)/10" \
| bc -l | sed 's/^\./0./'`
	cpu_iowait=`echo "scale=2; (1000*${diff_cpu_iowait}/${diff_cpu_total}+5)\\
/10" | bc -l | sed 's/^\./0./'`
	cpu_irq=`echo "scale=2; (1000*${diff_cpu_irq}/${diff_cpu_total}+5)/10" \
| bc -l | sed 's/^\./0./'`
	cpu_softirq=`echo "scale=2; (1000*${diff_cpu_softirq}/${diff_cpu_total}\\
+5)/10" | bc -l | sed 's/^\./0./'`
	cpu_total=`echo "scale=2; (1000*${diff_cpu_total}/${diff_cpu_total}+5)\\
/10" | bc -l | sed 's/^\./0./'`
	cpu_usage=`echo "(${cpu_user}+${cpu_nice}+${cpu_sys}+${cpu_iowait}+\\
${cpu_irq}+${cpu_softirq})/1" | bc`
}

do_output() {
	output="user: ${cpu_user}, nice: ${cpu_nice}, sys: ${cpu_sys}, \
iowait: ${cpu_iowait}, irq: ${cpu_irq}, softirq: ${cpu_softirq} \
idle: ${cpu_idle}"
}

do_perfdata() {
	perfdata="'user'=${cpu_user} 'nice'=${cpu_nice} 'sys'=${cpu_sys} \
'softirq'=${cpu_softirq} 'iowait'=${cpu_iowait} 'irq'=${cpu_irq} \
'idle'=${cpu_idle}"
}

if [ -n "$warn" -a -n "$crit" ]
then
    val_wcdiff
    if [ "$wcdiff" = 1 ]
    then
		echo "Please adjust your warning/critical thresholds. The warning\\
must be lower than the critical level!"
        exit $ST_UK
    fi
fi

get_cpuvals
do_output
do_perfdata

if [ -n "$warn" -a -n "$crit" ]
then
    if [ "$cpu_usage" -ge "$warn" -a "$cpu_usage" -lt "$crit" ]
    then
		echo "WARNING - ${output} | ${perfdata}"
        exit $ST_WR
    elif [ "$cpu_usage" -ge "$crit" ]
    then
		echo "CRITICAL - ${output} | ${perfdata}"
        exit $ST_CR
    else
		echo "OK - ${output} | ${perfdata}"
        exit $ST_OK
    fi
else
	echo "OK - ${output} | ${perfdata}"
    exit $ST_OK
fi
EOF
chmod a+rx $PLUGINDIR/check_cpu.sh

cat << EOF > $NRPE_D/check_cpu.cfg
command[check_cpu]=/usr/lib/nagios/plugins/check_cpu.sh
EOF
}

configure_ok_bundle() {
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

chmod a+rx $PLUGINDIR/check_procs.sh


}


if [ "$DISTRO" == "opensuse" ]; then
	PLUGINDIR=/usr/lib64/nagios/plugins/
	NRPE_USER=nagios
	if [ $HOSTTYPE == "i686" ]; then
		PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
	fi	
	NRPE_D=/etc/nrpe.d/
	install_opensuse;

elif [[ "$DISTRO" =~ fedora1[78] ]]; then
	PLUGINDIR=/usr/lib64/nagios/plugins/
	NRPE_USER=nrpe
	if [ $HOSTTYPE == "i686" ]; then
		PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
	fi	
	NRPE_D=/etc/nrpe.d/
	install_rhel;
elif [[ "$DISTRO" =~ rhel[5678] ]]; then
	PLUGINDIR=/usr/lib64/nagios/plugins/
	NRPE_USER=nrpe
	if [ $HOSTTYPE == "i686" ]; then
		PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
	fi	
	NRPE_D=/etc/nrpe.d/
	install_rhel;
elif [[ "$DISTRO" =~ centos[5678] ]]; then
        REPO=
        PLUGINDIR=/usr/lib64/nagios/plugins/
        NRPE_USER=nrpe
        if [ $HOSTTYPE == "i686" ]; then
                PLUGINDIR=`echo $PLUGINDIR | sed 's/lib64/lib/'`
        fi
        NRPE_D=/etc/nrpe.d/
        install_rhel;
elif [[ "$DISTRO" =~ "debian" ]]; then
	PLUGINDIR=/usr/lib/nagios/plugins/
	NRPE_D=/etc/nrpe.d
	NRPE_USER=nagios
	install_debian
elif [[ "$DISTRO" =~ "raspbian" ]]; then
	PLUGINDIR=/usr/lib/nagios/plugins/
	NRPE_D=/etc/nrpe.d
	NRPE_USER=nagios
	install_debian
elif [[ "$DISTRO" =~ "ubuntu" ]]; then
	PLUGINDIR=/usr/lib/nagios/plugins/
	NRPE_D=/etc/nrpe.d
	NRPE_USER=nagios
	install_debian
else
	echo could not detect distribution. Exiting...
	exit 1
fi
