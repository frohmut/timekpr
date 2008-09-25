#!/usr/bin/env python
import getpass, re
from time import strftime, sleep, localtime
from os.path import isfile, isdir, getmtime
from os import popen, mkdir, kill, isfile

# Copyright / License:
# Copyright (c) 2008 Chris Jackson <chris@91courtstreet.net>
# Further developed by:	Even Nedberg <code@nedberg.net>
#			Savvas Radevic <vicedar@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# See <http://www.gnu.org/licenses/>. 
#

## CONFIGURE START - You can change the following values:

# This is the grace period, where a notification pops up letting the users
# know that their time usage will be over soon.
# Users are given by default 120 seconds to finish up their work.
# Limit is expressed in seconds, e.g. 120 means 2 minutes
GRACEPERIOD = 120

# How often should the script check the timelogs.
# Setting is expressed in seconds, e.g. 45 means 45 seconds.
POLLTIME = 45

#Create a log?
DEBUGME = True
LOGFILE = '/var/log/timekpr.log'

#Default lock period
#Setting can be day(s), hour(s), minute(s)
#Example: 5 hours
LOCKLASTS = '1 hour'

## CONFIGURE END - Do not edit after this line!

#Check if admin
if getpass.getuser() != "root":
	exit('Error: You do not have administrative privileges')

#Default directory (for per-user configuration)
TIMEKPRDIR = '/etc/timekpr'

#Default configuration file (for timekpr variables)
TIMEKPRCONF = '/etc/timekpr.conf'

#Default working directory (for .logout, .lock, etc. files)
#I think we will still need them, in case they wish to revert the
#changes done by timekpr (unlock account, grant time, etc)
TIMEKPRWORK = '/var/lib/timekpr'

#TO-DO
#Check if it exists, if not, create it
if not os.path.isdir(TIMEKPRDIR):
	os.mkdir(TIMEKPRDIR)
if not os.path.isdir(TIMEKPRWORK):
	os.mkdir(TIMEKPRWORK)
if not os.path.isfile(TIMEKPRCONF):
	exit('Error: Could not find configuration file ' + TIMEKPRCONF)

#Read configuration file TIMEKPRCONF (re module)
#Security note: These values should be read only when running timekpr, not on the fly
def readconf(conffile):
	f = open(conffile, 'r')
	filevars = re.compile('^\s*((?:GRACEPERIOD|POLLTIME|DEBUGME|LOGFILE|LOCKLASTS)\s*=\s*.*)\s*$',re.M).findall( f.read(), 1)
	f.close()
	#More secure, variable names or values should not contain characters: ()[]
	for i in filevars:
		if re.compile('[()\[\]]').search(i):
			exit('Error: Found ()[] characters in ' + conffile + ' - ' + i)
	return filevars

#Import variables
for i in readconf(TIMEKPRCONF):
	exec i
#Imported variables: GRACEPERIOD, POLLTIME, DEBUGME, LOGFILE, LOCKLASTS

#Ubuntu uses alternatives so we look for x-session-manager instead of gnome-session
SESSION_MANAGER = 'x-session-manager'

def logkpr(string,clear=0):
	#To log: logkpr("Something")
	#To clear file and log: logkpr("Something",1)
	if clear == 1:
		l = open(LOGFILE, 'w')
	else:
		l = open(LOGFILE, 'a')
	nowtime = time.strftime('%Y-%m-%d %H:%M:%S ', time.localtime())
	l.write(nowtime + string +'\n')

def logOut(user,pid):
	#Forces the user to log out.
	if issessionalive(user) == 1:
		logkpr('logOut: Attempting killing '+user+' (TERM, 15)...')
		#this is a pretty bad way of killing a gnome-session, but we warned 'em
		#Should it be signal 1 (HUP)?
		os.kill(pid,15)
		time.sleep(5)
		if issessionalive(user) == 1:
			logkpr('logOut: Process still there, attempting force-killing '+user+' (KILL, 9)...')
			os.kill(pid,9)
		#logkpr('logOut: touched $username.logout')
		#touched?
	
	""" uncomment the following to brutally kill all of the users processes
		sleep 5
		pkill -u $username
	# killing gnome-session should be more like:
	DISPLAY=":0" XAUTHORITY="/tmp/.gdmEQ0V5T" SESSION_MANAGER="local/wretched:/tmp/.ICE-unix/$pid" su -c 'gnome-session-save --kill --silent' $username
	# but this can still leave processes to cleanup - plus it's not easy to get SESSION_MANAG
	"""

def lockacct(user):
	

def checklockacct():
	

def fileisok(fname):
	#File exists and is today's?
	if (os.isfile(fname)) and fromtoday(fname):
		return True
	return False

def readusersettings(conffile):
	#Returns limits and from/to allowed hours
	fhandle = open(conffile)
	limits = fhandle.readline() #Read 1st line
	bfrom = fhandle.readline() #Read 2nd line
	bto = fhandle.readline()
	"""Deprecated
	limits = limits.replace("limit=( ","")
	limits = limits.replace(" )", "")
	limits = limits.split(" ")
	bfrom = bfrom.replace("from=( ", "")
	bfrom = bfrom.replace(" )", "")
	bfrom = bfrom.split(" ")
	bto = bto.replace("to=( ", "")
	bto = bto.replace(" )", "")
	bto = bto.split(" ")
	"""
	limits = re.compile('(\d+)').findall(limits)
	bfrom = re.compile('(\d+)').findall(bfrom)
	bto = re.compile('(\d+)').findall(bto)
	return limits, bfrom, bto

def getcmdoutput(cmd):
	#Execute a command, returns its output
	out = os.popen(cmd)
	return out.read()

def getsessions():
	#Returns sessions that run x-session-manager: ['username', 'pid']
	#Needs: ps
	#for uname, pid in getsessions():
	#	print "username="+uname+" pid="+pid
	sessionsraw = getcmdoutput('ps --no-headers -fC x-session-manager')
	sessions = re.compile('^([^\s+]+)\s+([^\s+]+)',re.M).findall(sessionsraw)
	return sessions

def issessionalive(user):
	# Checking if session process still running
	# Should it check against username and pid?
	# Returns:	1 if process is still there (user logged in),
	#		0 if user has logged out
	for u,p in getsessions():
		if u == user:
			return 1
	return 0

def getdbus(pid):
	#Returns DBUS_SESSION_BUS_ADDRESS variable from /proc/pid/environ
	pid = str(pid)
	p = open('/proc/'+pid+'/environ', 'r')
	i = re.compile('(DBUS_SESSION_BUS_ADDRESS=[^\x00]+)').findall(p.read())
	p.close()
	return i[0]
	#Returns: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7
	#Note:	If you would use [^,] in regex you would get: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw

def notify(username, pid, title, message):
	"""
	Sends a notification via notify-send
	Usage: sendnotification( "youruser", "pid", "your title", "your message")
	We will be probably using pynotify module for this, we'll see!
	"""
	#WARNING: Don't use the exclamation mark ("!") in the message or title, otherwise bash will return something like:
	# -bash: !": event not found
	#Might be good to include these substitutions, if someone doesn't read this warning
	title = re.compile('!').sub('\!', title)
	message = re.compile('!').sub('\!', message)
	#Get DBus
	dbus = getdbus(pid)
	#Create and send command
	notifycmd = 'su %s -c "%s notify-send \\"%s\\" \\"%s\\""' % (username, dbus, title, message)
	getcmdoutput(notifycmd)
	
	"""The long representations in terminal:
	# su username -c "DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send \"title\" \"message\""
	# sudo -u username DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send "title" "message"
	"""

def gettime(tfile):
	#Adds time to the timefile
	if fileisok(tfile):
		logkpr('This day\'s ' + username + '.time file exists, adding time')
		t = open(tfile)
	else:
		t = open(tfile, 'w+')
	newtime = t.readline() + POLLTIME
	writetime(tfile, newtime)
	return newtime

def writetime(tfile, time):
	#Write time to timefile
	f = open(tfile, 'w')
	f.write(time)

def fromtoday(fname):
	#Is the file today's?
	fdate = time.strftime("%Y%m%d", time.localtime(os.path.getmtime(fname)))
	today = time.strftime("%Y%m%d", time.localtime())
	return fdate == today

logkpr('Starting timekpr',1)

while (True):
	# Check if any accounts should be unlocked and re-activate them
	checklockacct()
	# Get the usernames and PIDs of sessions
	for username, pid in getsessions():
		conffile = TIMEKPRDIR + '/' + username
		# Check if user configfile exists, if it doesn't the user is unrestricted and we need not check any more
		if os.path.isfile(conffile):
			logkpr('conffile of ' + username + 'exists')
			# Read lists: from, to and limit
			limits, bfrom, bto = readusersettings(conffile)
			timefile = TIMEKPRDIR + '/' + username + '.time'
			allowfile = TIMEKPRDIR + '/' + username + '.allow'
			latefile = TIMEKPRDIR + '/' + username + '.late'
			logoutfile = TIMEKPRDIR + '/' + username + '.logout'
		
			time = gettime(timefile)
			'''Is the user allowed to be logged in at this time?
			We take it for granted that if they are allowed to login all day ($default_limit) then
			they can login whenever they want, ie they are normal users'''
			
			# Get current day index and hour of day
			index = int(time.strftime("%w", time.localtime()))
			hour = time.strftime("%H", time.localtime())
			
			logkpr('User ' + username + ' PID ' + pid + ' Day-Index: ' + index + ' Seconds-passed: ' + time)
			
			# Compare: is current hour less than the one in bfrom list?
			if hour < bfrom[index]:
				if os.isfile(allowfile):
					logkpr('Current hour less than the defined hour in conffile for user: ' + username)
					if not fromtoday(allowfile):
					logkpr('Extended login hours detected from ' + username + '.allow, but not from today')
					logOut(username, pid)
					os.remove(allowfile)
				else:
					# User has not been given extended login hours
					logkpr('Extended hours not detected, ' + username + ' not in allowed period from-to')
					logOut(username, pid)
			
			# Compare: is current hour greater/equal to $to array?
			if hour > bto[index]:
				logkpr('Current hour greater than the defined hour in conffile for user: ' + username)
				# Has the user been given extended login hours?
				if os.isfile(allowfile):
					if not fromtoday(allowfile):
					logkpr('Extended login hours detected from ' + username + '.allow, but not from today')
					# Has the user been late-kicked today?
					if os.isfile(latefile):
						if fromtoday(latefile):
							logkpr('User: ' + username + ' has been late-kicked today')
							logOut(username, pid)
							os.remove(allowfile)
							#Lock account
							lockacct(username)
						else:
							logkpr('User: ' + username + ' has NOT been late-kicked today')
							notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + bfrom[index] + ' and ' + bto[index] + '.')
							logOut(username, pid)
							open(latefile, 'w')
							os.remove(allowfile)
					else:
					logkpr('Extended login hours detected ' + username + '.allow is from today')
				else:
					# User has not been given extended login hours
					logkpr('Extended hours not detected, ' + username + ' not in allowed period from-to')
					if os.isfile(latefile) and fromtoday(latefile):
						logkpr('User: ' + username + ' has been late-kicked today')
						logOut(username, pid)
						#Lock account
						lockacct(username)
					else:
						logkpr('User: ' + username + ' has NOT been late-kicked today')
						notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + bfrom[index] + ' and ' + bto[index] + '.')
						logOut(username, pid)
						open(latefile, 'w')
			
			# Is the limit exeeded
			if time > limits[index]:
				logkpr('Exceeded todays limit, user: ' + username)
				# Has the user already been kicked out?
				if os.isfile(logoutfile):
					# Was he kicked out today?
					if fromtoday(logoutfile):
						logkpr(username + ' has been kicked out today')
						logOut(username, pid)
						#Lock account
						lockacct(username)
					else:
						# The user has not been kicked out today
						logkpr(username + ' has been kicked out, but not today')
						notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit')
						logOut(username, pid)
						open(logoutfile, 'w')
				else:
					# The user has not been kicked out before
					logkpr('Not found: ' + username + '.logout')
					notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit')
					logOut(username, pid)
					open(logoutfile, 'w')
	
	# Done checking all users, sleeping
	logkpr('Finished checking all users, sleeping for ' + POLLTIME + ' seconds')
	time.sleep(POLLTIME)