#!/usr/bin/env python
import os.path, getpass, re, time
from os import popen, mkdir

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
allvars = readconf(TIMEKPRCONF)
for i in allvars:
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

def notify(user, message):
	

def logOut(user):
	

def lockacct(user):
	

def checklockacct():
	

def fileisok(filename):
	exists = os.isfile(filename)
	filedate = time.strftime("%Y%m%d", time.localtime(os.path.getmtime(filename)))
	today = time.strftime("%Y%m%d", time.localtime())
	if (exists) and (filedate == today):
		return True
	else:
		return False


def readusersettings(conffile):
	fileHandle = open(configFile)
	limits = fileHandle.readline()
	bfrom = fileHandle.readline()
	bto = fileHandle.readline()
	limits = limits.replace("limit=( ","")
	limits = limits.replace(")", "")
	limits = limits.split(" ")
	bfrom = bfrom.replace("from=( ", "")
	bfrom = bfrom.replace(")", "")
	bfrom = bfrom.split(" ")
	bto = bto.replace("to=( ", "")
	bto = bto.replace(")", "")
	bto = bto.split(" ")
	return limits, bfrom, bto


def getcmdoutput(cmd):
	#Execute a command, returns its output
	out = os.popen(cmd)
	return out.read()

def getsessions():
	#Returns sessions that run x-session-manager
	#Needs: ps
	#for uname, pid in getsessions():
	#	print "username="+uname+" pid="+pid
	sessionsraw = getcmdoutput('ps --no-headers -fC x-session-manager')
	sessions = re.compile('^([^\s+]+)\s+([^\s+]+)',re.M).findall(sessionsraw)
	return sessions

def getdbus(pid):
	#Returns DBUS_SESSION_BUS_ADDRESS variable from /proc/pid/environ
	pid = str(pid)
	p = open('/proc/'+pid+'/environ', 'r')
	i = re.compile('(DBUS_SESSION_BUS_ADDRESS=[^\x00]+)').findall(p.read())
	p.close()
	return i[0]
	#Returns: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7
	#Note:	If you would use [^,] in regex you would get: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw

def sendnotification(username, pid, title, message):
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
	'''The long representations in terminal:
	# su username -c "DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send \"title\" \"message\""
	# sudo -u username DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send "title" "message"
	'''

logkpr('Starting timekpr',1)

while (True):
	#check if any accounts should be unlocked and re-activate them
	checklockacct()
	# get the usernames and PIDs of sessions
	for username, pid in getsessions():
		conffile = TIMEKPRDIR + '/' + username
		# check if user configfile exists
		if os.isfile(conffile):
			logkpr('conffile of ' + username + 'exists')
			# Read lists: from, to and limit
			limits, bfrom, bto = readusersettings(conffile)
			timefile = TIMEKPRDIR + '/' + username + '.time'
			allowfile = TIMEKPRDIR + '/' + username + '.allow'
			latefile = TIMEKPRDIR + '/' + username + '.late'
			
			if fileisok(timefile):
				logkpr('This days ' + username + '.time file exists, adding time')

