#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage $(basename $0) <username> <time to add in minutes>"
	exit
fi  

adj=$(($2*60))
now=$(cat /var/lib/timekpr/$1.time)
new=$(($now-$adj))
echo $new > /var/lib/timekpr/$1.time
limit=$(cat /var/lib/timekpr/$1)
left=$(($limit-$new))
echo
echo "$2 minute(s) added to ${1}s account."
echo "$1 now has $(($left/60)) minute(s) left."
echo

