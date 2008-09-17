#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage $(basename $0) <username>"
	exit
fi

if [[ -e "/var/lib/timekpr/$1.allow" ]]; then
	rm "/var/lib/timekpr/$1.allow"
	echo
	echo "$1 has been disallowed to log in outside of normal logon hours"
	echo
else
	touch /var/lib/timekpr/$1.allow
	echo
	echo "$1 has been allowed to log in outside of normal logon hours"
	echo
fi

