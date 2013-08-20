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
  echo
fi

trap "rm -f ${TMPDIR}/authinfo" EXIT
cat <<EO > ${TMPDIR}/authinfo
username=${DOMAIN_USER}
password=${DOMAIN_PASSWORD}
domain=${DOMAIN}
EO

function fatal_error() {
	msg=$1
	echo -e "Error, ${msg}\n" >&2
	exit 1
}

printf "[%-20s]($(hostname)) " "Check Prerequisites"
if [ ! -d "${INSTALL_LOCATION}/nsclient" ]; then
	fatal_error "Directory $INSTALL_LOCATION/nsclient not found\nMore info at https://github.com/opinkerfi/okconfig/wiki/Deploying-nsclient-on-windows-servers"
fi

echo OK

for i in $HOSTLIST ; do

	printf "[%-20s](${i}) " "Connection test"
	winexe --reinstall -d 1 -A ${TMPDIR}/authinfo "//$i" "cmd /c echo test" 2>&1 >> $TMPDIR/install.log 
	if [ $RESULT -gt 0 ]; then
		fatal_error "Error: connection test failed, check ${TMPDIR}/install.log"
		exit 1
	fi
	echo OK

	# Stop run, we can connect
	if [ $TEST -gt 0 ]; then
		exit 0
	fi

	printf "[%-20s](${i}) " "Upload NSClient++ Setup"

	winexe --reinstall -d 0 -A ${TMPDIR}/authinfo "//$i" "cmd /c md c:\temp 2>NUL" 2>&1 >> $TMPDIR/install.log
	winexe --reinstall -d 0 -A ${TMPDIR}/authinfo "//$i" "cmd /c rd c:\temp\nsclient /Q /S" 2>&1 >> $TMPDIR/install.log

	cd $INSTALL_LOCATION
	
	smbclient -d 0 //$i/c$ -A ${TMPDIR}/authinfo -c  "cd /temp ; recurse ; prompt ; mput nsclient" 2>&1 >> $TMPDIR/install.log
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		fatal_error "Error: Failed to copy files to $i, check ${TMPDIR}/install.log"
		exit 1
	fi
	echo OK
	
	echo "[%-20s](${i}) " "Installing NSClient++"
	winexe --reinstall -d 0 -A ${TMPDIR}/authinfo "//$i" "cmd /c $BATCHFILE" 2>&1 >> $TMPDIR/install.log
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		fatal_error "install of $i failed, check ${TMPDIR}/install.log"
		exit 1
	fi
	echo OK
done

rm -f ${TMPDIR}/*.log ${TMPDIR}/authinfo
rmdir ${TMPDIR}

exit 0

