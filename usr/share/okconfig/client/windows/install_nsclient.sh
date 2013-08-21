#!/bin/sh

BATCHFILE='c:\temp\nsclient\install.bat'
AUTHFILE=$(mktemp /tmp/okconfig.XXXXXXXXXX)
INSTALL_LOCATION=/usr/share/okconfig/client/windows/
LOGFILE=/var/log/okconfig/install_nsclient.log
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
	"--authentication-file" | "-A")
		USER_AUTHFILE="$1" ; shift ;;
	*)
		HOSTLIST="$HOSTLIST $arg"  ;;

	esac
done

if [ -z "${USER_AUTHFILE}" ]; then
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
	trap "rm -f ${AUTHFILE}" EXIT
	cat <<EO > ${AUTHFILE}
username=${DOMAIN_USER}
password=${DOMAIN_PASSWORD}
domain=${DOMAIN}
EO
else
	DOMAIN=$(grep -i ^domain ${USER_AUTHFILE} |awk -F" = " '{print $2}')
	AUTHFILE="${USER_AUTHFILE}"
fi

function fatal_error() {
	stage=$1
        host=$2
	msg=$3
	printf "[%-24s] %s FATAL %s\n" "${stage}" "${host}" "${msg}" >&2
	echo -e "$(date -R): FATAL ${msg}\n" >> ${LOGFILE}
	exit 1
}

function error() {
	stage=$1
        host=$2
	msg=$3
	printf "[%-24s] %s ERROR %s\n" "${stage}" "${host}" "${msg}" >&2
	echo -e "$(date -R): ERROR ${msg}\n" >> ${LOGFILE}
}

function host_stage() {
        stage=$1
	host=$2
	printf "[%-24s] %s Starting..\n" "${stage}" "${host}"
	printf "$(date -R): [%-24s] %s Starting\n" "${stage}" "${host}" >> ${LOGFILE}
}

function OK() {
        stage=$1
        host=$2
	printf "[%-24s] %s %s\n" "${stage}" "${host}" "OK"
	printf "$(date -R): [%-24s] %s %s\n" "${stage}" "${host}" "OK" >> ${LOGFILE}
}

host_stage "Check Prerequisites" "$(hostname)"
if [ ! -d "${INSTALL_LOCATION}/nsclient" ]; then
	fatal_error "Check Prerequisites" "$(hostname)" "Directory $INSTALL_LOCATION/nsclient not found\nMore info at https://github.com/opinkerfi/okconfig/wiki/Deploying-nsclient-on-windows-servers"
fi

OK "Check Prerequisites" "$(hostname)"

function install_host() {
	local host
	host=$1
	host_stage "Connection test" "${host}"
	winexe --reinstall -d 1 -A ${AUTHFILE} "//${host}" "cmd /c echo test" 2>&1 | awk "{ print \"$(date -R): ${host}\", \$0}" >> ${LOGFILE}
        RESULT=${PIPESTATUS[0]}
	if [ $RESULT -gt 0 ]; then
		error "Connection test" "${host}" "Connection test failed, check ${LOGFILE}"
		continue
	fi
	OK "Connection test" "${host}"

	# Stop run, we can connect
	if [ $TEST -gt 0 ]; then
		exit 0
	fi

	host_stage "Upload NSClient++ Setup" "${host}"

	cd $INSTALL_LOCATION
	
	smbclient -d 0 //${host}/c$ -A ${AUTHFILE} -W ${DOMAIN} -c  "mkdir /temp ; mkdir /temp ; cd /temp ; recurse ; prompt ; mput nsclient" 2>&1 | awk "{ print \"$(date -R): ${host}\", \$0}" >> ${LOGFILE}
	RESULT=${PIPESTATUS[0]}
	
	if [ $RESULT -gt 0 ]; then
		error "Upload NSClient++ Setup" "${host}" "Failed to copy files to ${host}, check ${LOGFILE}"
		continue
	fi
	OK "Upload NSClient++ Setup" "${host}"
	
	host_stage "Installing NSClient++" "${host}"
	winexe --reinstall -d 0 -A ${AUTHFILE} "//${host}" "cmd /c $BATCHFILE" 2>&1 | awk "{ print \"$(date -R): ${host}\", \$0}" >> ${LOGFILE}
	RESULT=${PIPESTATUS[0]}
	
	if [ $RESULT -gt 0 ]; then
		error "Installing NSClient++" "${host}" "install of ${host} failed, check ${LOGFILE}"
		continue
	fi
	OK "Installing NSClient++" "${host}"
}

for i in $HOSTLIST ; do
	install_host "${i}"
done

exit 0

