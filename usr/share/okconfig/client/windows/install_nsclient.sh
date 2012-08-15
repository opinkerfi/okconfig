#!/bin/sh

DOMAIN=""
DOMAIN_USER=""
DOMAIN_PASSWORD=""
HOSTLIST=""
BATCHFILE='c:\temp\nsclient\install.bat'
TMPFILE=`mktemp`
INSTALL_LOCATION=/usr/share/okconfig/client/windows/

while [ $# -gt 0 ]; do
	arg=$1 ; shift
	case $arg in
	"--domain")
		DOMAIN=$1 ; shift ;;
	"--user")
		DOMAIN_USER="$1" ; shift;;
	"--password")
		DOMAIN_PASSWORD="$1" ; shift;;
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

for i in $HOSTLIST ; do
	echo "Starting install of $i ... " 
	echo "Preparing client for copy ..."

	winexe --reinstall -d -1 -U "$DOMAIN/$DOMAIN_USER%$DOMAIN_PASSWORD" "//$i" "cmd /c md c:\temp 2>NUL" >> $TMPFILE
	winexe --reinstall -d -1 -U "$DOMAIN/$DOMAIN_USER%$DOMAIN_PASSWORD" "//$i" "cmd /c rd c:\temp\nsclient /Q /S" >> $TMPFILE

	echo "Copying files to remote server..."
	cd $INSTALL_LOCATION
	
	if [ ! -d nsclient ]; then
		echo "Error: Directory $INSTALL_LOCATION/nsclient not found" >&2
		exit 1
	fi
	smbclient -d 0 //$i/c$ "$DOMAIN_PASSWORD" -W "$DOMAIN" -U "$DOMAIN_USER" -c  "cd /temp ; recurse ; prompt ; mput nsclient"
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		echo Error: Failed to copy files to $i >&2
		exit 1
	else
		echo "Files have been copied to $i"
	fi
	
	echo "Executing install script..."
	winexe --reinstall -d -1 -U "$DOMAIN/$DOMAIN_USER%$DOMAIN_PASSWORD" "//$i" "cmd /c $BATCHFILE" >> $TMPFILE
	RESULT=$?
	
	if [ $RESULT -gt 0 ]; then
		echo install of $i failed >&2
		cat $TMPFILE 
		exit 1
	else
		echo "Install of $i sucessful" 
	fi
done
exit 0

