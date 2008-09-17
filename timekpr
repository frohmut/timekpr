#!/bin/bash
###
# timekpr.sh - simple 
# watches gnome sessions and logs them out once the user has exceeded a set, per day limit
# /var/lib/timekpr/$username.time hold a count of seconds user has had a gnome session
# /var/lib/timekpr/$username hold the daily allowed seconds for the user and other configurations
#
# you may need to install notify-send with: $apt-get install libnotify-bin
#
# Copyright 2008 Chris Jackson <chris@91courtstreet.net>
# Further developed by Even Nedberg <code@nedberg.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See <http://www.gnu.org/licenses/>. 
#

default_limit=86400 # All day, new users is given this value
grace_period=120 # how much time do we give to let the user log out?
poll_time=45 # How often the script should check the timelogs
#from=7 # When is the users allowed to log in
#to=22 # When is the users no longer allowed to be loged in


#Ubuntu uses alternatives so we look for x-session-manager instead of gnome-session
SESSION_MANAGER=x-session-manager

function notify() {
## get the display and xauthority used by out session manager
	UDISPLAY=`grep -z DISPLAY \
		/proc/$pid/environ | sed -e 's/DISPLAY=//'`
	XAUTHORITY=`grep -z XAUTHORITY \
		/proc/$pid/environ | sed -e 's/XAUTHORITY=//'`
		
	# find DBUS session bus for this session
	DBUS_SESSION_BUS_ADDRESS=`grep -z DBUS_SESSION_BUS_ADDRESS \
		/proc/$pid/environ | sed -e 's/DBUS_SESSION_BUS_ADDRESS=//'`
	# use it - give a warning, then another one 1/2 way through grace_period
	XAUTHORITY="$XAUTHORITY" DISPLAY="$UDISPLAY" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
		notify-send --icon=gtk-dialog-warning --urgency=critical -t 10000 "$1" "Your session is about to expire! You have $(($grace_period/60)) minutes to save your work and log out."
	sleep $(($grace_period/2))   # FIXME: this gives other sessions a free grace_period added to their accounting
	echo -ne "\007"
	XAUTHORITY="$XAUTHORITY" DISPLAY="$UDISPLAY" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
		notify-send --icon=gtk-dialog-warning --urgency=critical -t 10000 "$1" "Your session is about to expire! You have $(($grace_period/120)) minutes to save your work and log out."
	sleep $(($grace_period/2))   # FIXME: this gives other sessions a free grace_period added to their accounting
	echo -ne "\007"
	XAUTHORITY="$XAUTHORITY" DISPLAY="$UDISPLAY" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
		notify-send --icon=gtk-dialog-warning --urgency=critical -t 10 "Shutting Down" "Shutting down session ($pid) now!" 
}

function logOut() {
# FIXME - should really check to see if user has logged out yet 
	kill -HUP $pid    #this is a pretty bad way of killing a gnome-session, but we warned 'em
	touch /var/lib/timekpr/$username.logout

## uncomment the following to  brutally kill all of the users processes
#	sleep 5
#	pkill -u $username

## killing gnome-session should be more like:
	#DISPLAY=":0" XAUTHORITY="/tmp/.gdmEQ0V5T" SESSION_MANAGER="local/wretched:/tmp/.ICE-unix/$pid" su -c 'gnome-session-save --kill --silent' $username
## but this can still leave processes to cleanup - plus it's not easy to get SESSION_MANAGER

}


while(true); do
# get the usernames and PIDs of sessions
	pidlists=$( ps --no-heading -fC $SESSION_MANAGER | awk 'BEGIN{ FS=" " } { print $1 "," $2 }' )
	for pidlist in $pidlists; do
		
		# split username and pid - FIXME - I bet this would be faster with bash arrays and substitution 
		username=$( echo $pidlist | awk 'BEGIN{ FS=","} { print $1}' )
		pid=$( echo $pidlist | awk 'BEGIN{ FS=","} { print $2}' )
			
		# If the user is not enabled, give him $default_limit
		if [[ -e "/var/lib/timekpr/$username" ]]; then
			source /var/lib/timekpr/$username

			if [[ -e "/var/lib/timekpr/$username.time" && `( stat -c '%z' /var/lib/timekpr/$username.time | cut -c9,10 )` == `date +%d` ]]; then
				# the time file exists and was last touched today, add $poll_time seconds to it
				timekpr=$(( `cat /var/lib/timekpr/$username.time` + $poll_time ))
				echo $timekpr > /var/lib/timekpr/$username.time
			else  # the time file is missing or was last touched yesterday
				timekpr=$poll_time
				echo $timekpr > /var/lib/timekpr/$username.time
			fi

			echo $username, $pid, $timekpr
			
			# Is the user allowed to be loged in at this time?
			# We take it for granted that if they are allowed to log in all day ($default_limit) then
			# they can log in whenever they want, ie they are normal users
			
			# Get the index for the current day
			index=$(date +%w)
			
			if ( [[ $(date +%k) -lt ${from[$index]} ]] || [[ $(date +%k) -ge ${to[$index]} ]] ); then
				# Has the user been given extended log in hours?
				if [[ -e "/var/lib/timekpr/$username.allow" ]]; then
					# Was the extended log in hours given today?
					if [[ $(stat -c '%z' /var/lib/timekpr/$username.allow | cut -c1-10) != $(date +%Y-%m-%d) ]]; then
						notify "Only log in between ${from[$index]} and ${to[$index]}"
						logOut
						rm /var/lib/timekpr/$username.allow
					fi
				else
					# User has not been given extended log in hours
					notify "Only log in between ${from[$index]} and ${to[$index]}"
					logOut
				fi
			fi
			
		
			# Is the limit exeeded
			if [[ $timekpr -ge ${limit[$index]} ]]; then
				# Has the user already been kicked out?
				if [[ -e "/var/lib/timekpr/$username.logout" ]]; then
					# Was he kicked out today?
					if [[ $(stat -c '%z' /var/lib/timekpr/$username.logout | cut -c1-10) == $(date +%Y-%m-%d) ]]; then
						logOut
					else
						# The user has not been kicked out today
						notify "Daily time limit"
						logOut
					fi
				else
					# The user has not been kicked out today
					notify "Daily time limit"
					logOut
				fi
			fi
		fi
	done
	# Wait a while before we check again
	sleep $poll_time
done
