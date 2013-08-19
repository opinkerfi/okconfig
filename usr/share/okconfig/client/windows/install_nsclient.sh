#!/bin/sh

BATCHFILE='c:\temp\nsclient\install.bat'
TMPDIR=$(mktemp -d /tmp/okconfig.XXXXXXXXXX)
INSTALL_LOCATION=/usr/share/okconfig/client/windows/
TEST=0

while [ $# -gt 0 ]; do
	arg=$1 ; shift
	case $arg in
	"--domain")
		DOMAIN=$1 ; shift ;;
	"--user")
		DOMAIN_USER="$1" ; shift;;
	"--password")
		DOMAIN_PASSWORD="$1" ; shift;;
	"--test")
		TEST=1
		;;
	*)
		HOSTLIST="$HOSTLIST $arg"  ;;

	esac
done


if [ -z "$DOMAIN" ]; then
	echo -n "Domain Name (DOMAIN): "
	read DOMAIN
fi


if [ -z "$DOMAIN_USER" ]; then
  echo -n "Domain user (user): "
  read DOMAIN_USER
fi


if [ -z "$DOMAIN_PASSWORD" ]; then
  stty -echo
  echo -n "Domain password: "
  read DOMAIN_PASSWORD
  stty echo
fi

trap "rm -f ${TMPDIR}/authinfo" EXIT
cat <<EO > ${TMPDIR}/authinfo
username=${DOMAIN_USER}
password=${DOMAIN_PASSWORD}
domain=${DOMAIN}
EO

if [ ! -d "${INSTALL_LOCATION}/nsclient" ]; then
	echo "Error: Directory $INSTALL_LOCATION/nsclient not found" >&2
	exit 1
fi

for i in $HOSTLIST ; do
	echo "Executing connection test with ${i}..."
	winexe --reinstall -d -1 -A ${TMPDIR}/authinfo "//$i" "cmd /c echo test" 2>&1 >> $TMPDIR/install.log 
	RESULT=$?
	if [ $RESULT -gt 0 ]; then
		echo "Error: connection test failed, check ${TMPDIR}/install.log" >&2
		exit 1
	fi
	# Stop run, we can connect
	if [ $TEST -gt 0 ]; then
		echo "Success connecting"
		exit 0
	fi

	echo "Starting install of $i ... " 
	echo "Preparing client for copy ..."

	winexe --reinstall -d -1 -A ${TMPDIR}/authinfo "//$i" "cmd /c md c:\temp 2>NUL" >> $TMPDIR/install.log
	winexe --reinstall -d -1 -A ${TMPDIR}/authinfo "//$i" "cmd /c rd c:\temp\nsclient /Q /S" >> $TMPDIR/install.log

	echo "Copying files to remote server..."
	cd $INSTALL_LOCATION
	
	smbclient -d 0 //$i/c$ -A ${TMPDIR}/authinfo -c  "cd /temp ; recurse ; prompt ; mput nsclient"
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		echo Error: Failed to copy files to $i, check ${TMPDIR}/install.log >&2
		exit 1
	else
		echo "Files have been copied to $i"
	fi
	
	echo "Executing install script..."
	winexe --reinstall -d -1 -A ${TMPDIR}/authinfo "//$i" "cmd /c $BATCHFILE" >> $TMPDIR/install.log
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		echo install of $i failed, check ${TMPDIR}/install.log >&2
		exit 1
	fi
done

echo "Install of $i sucessful" 
rm -f ${TMPDIR}/*.log ${TMPDIR}/authinfo
rmdir ${TMPDIR}

exit 0

