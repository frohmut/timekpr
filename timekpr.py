#!/usr/bin/env python
""" The "daemon service" for timekpr.
	Copyright / License: See COPYRIGHT.txt
"""

import re
from time import strftime, sleep, localtime, mktime, time as timenow
from os.path import split as splitpath, isfile, isdir, getmtime
from os import popen, mkdir, kill, remove
from glob import glob
from threading import Timer

#If DEVACTIVE is true, it uses files from local directory
DEVACTIVE = False

#IMPORT
if DEVACTIVE:
	from sys import path
	path.append('.')
from timekprpam import * # timekprpam.py
from timekprcommon import * # timekprcommon.py

#timekpr.conf variables (dictionary variable)
VAR = getvariables(DEVACTIVE)

#Check if admin/root
checkifadmin()

#Check if it exists, if not, create it
if not isdir(VAR['TIMEKPRDIR']):
	mkdir(VAR['TIMEKPRDIR'])
if not isdir(VAR['TIMEKPRWORK']):
	mkdir(VAR['TIMEKPRWORK'])

# Lists keeping track of users who has been notified
notifiedusers = []

# Keep track of todays date
THISDAY = strftime("%Y%m%d")

def logkpr(string,clear = 0):
	#To log: logkpr("Something")
	#To clear file and log: logkpr("Something",1)
	if VAR['DEBUGME'] != 'True':
		return
	if clear == 1:
		l = open(VAR['LOGFILE'], 'w')
	else:
		l = open(VAR['LOGFILE'], 'a')
	nowtime = strftime('%Y-%m-%d %H:%M:%S ')
	l.write(nowtime + string +'\n')

def logOut(user, somefile = ''):
	logkpr('logOut called with user: %s and somefile: %s' % (user, somefile))
	if somefile != '':
		f = open(somefile, 'w').close()
	if issessionalive(user):
		logkpr('logOut: Attempting killing %s (SIGTERM)...' % user)
		#this is a pretty bad way of killing a users processes, but we warned 'em
		getcmdoutput('pkill -SIGTERM -u %s' % user)
		sleep(5)
		if issessionalive(user):
			logkpr('logOut: Process still there, attempting force-killing %s (SIGKILL)...' % user)
			getcmdoutput('pkill -SIGKILL -u %s' % user)


## Using Linux-PAM to lock and disable users
def getlocklasts():
	#Returns the VAR['LOCKLASTS'] variable in seconds
	t=re.compile('(\d+) (second|minute|hour|day|week|month|year)s?').match(VAR['LOCKLASTS'])
	if not t:
		exit('Error: locklasts value "%s" is badly formatted, should be something like "1 week" or "2 hours"' % VAR['LOCKLASTS'])
	#n = time length
	#m = second|minute|hour|day|week|month|year
	(n,m)=(int(t.group(1)),t.group(2))
	#variable dictionary: multiply
	multiply = {
		'second': n,
		'minute': n * 60,
		'hour': n * 60 * 60,
		'day': n * 60 * 60 * 24,
		'week': n * 60 * 60 * 24 * 7,
		'month': n * 60 * 60 * 24 * 30
	}
	#Return in seconds (integer)
	return multiply[m]

def lockacct(u):
	#Locks user and sets the date in a file
	logkpr('lockacct called for user %s' % u)
	lockfile = VAR['TIMEKPRDIR'] + '/' + u + '.lock'
	f = open(lockfile, 'w')
	f.close()
	lockuser(u) # timekprpam.py

def checklockacct():
	#Check if user should be unlocked and unlock them
	logkpr('checklockacct called')
	#Find *.lock in VAR['TIMEKPRDIR']
	s = VAR['TIMEKPRDIR'] + '/*.lock'
	l = glob(s)
	for f in l:
		#Get username from filename - os.path.split
		u = splitpath(f)[1].replace('.lock', '')
		lastmodified = getmtime(f) #Get last modified time from username.lock file
		#Get time when lock should be lifted
		dtlock = float(lastmodified + getlocklasts())
		dtnow = float(timenow())
		#If time now is great than or equal to the time when lock should be lifted
		if dtnow >= dtlock:
			logkpr('checklockacct: %s should be unlocked, unlocking..' % u)
			unlockuser(u)
			logkpr('checklockacct: removing %s.lock file..' % u)
			remove(f)

## File defs
def fileisok(fname):
	#File exists and is today's?
	if isfile(fname) and fromtoday(fname):
		return True
	return False

def getusers():
	u = getcmdoutput('users.timekpr')
	u = u.split()
	u = set(u)
	return list(u)

def issessionalive(user):
	# Checking if session process still running
	# Should it check against username and pid?
	# Returns:	True if process is still there (user logged in),
	#		False if user has logged out
	for u in getusers():
		if u == user:
			return True
	return False

def gettime(tfile, username):
	#Adds time to the timefile
	if fileisok(tfile):
		logkpr("This day\'s %s.time file exists, adding time" % username)
		t = open(tfile)
		newtime = int(t.readline()) + VAR['POLLTIME']
	else:
		t = open(tfile, 'w')
		newtime = VAR['POLLTIME']
	t.close()
	writetime(tfile, newtime)
	return newtime

def writetime(tfile, time):
	#Write time to timefile
	f = open(tfile, 'w')
	f.write(str(time))

def threadit(sleeptime, command, *args):
	t = Timer(sleeptime, command, args)
	t.start()

def addnotified(u):
	#Adds username to notifiedusers list, so it does not re-notify them
	try:
		notifiedusers.index(u)
	except ValueError:
		notifiedusers.append(u)

def isnotified(u):
	#Checks if username is already in notifiedusers list
	try:
		notifiedusers.index(u)
	except ValueError:
		return False
	return True

def removenotified(u):
	#Removes username from notifiedusers list, so it does not re-notify them
	try:
		notifiedusers.index(u)
	except ValueError:
		return
	notifiedusers.remove(u)

logkpr('Starting timekpr version %s' % getversion())
logkpr('Variables: GRACEPERIOD: %s POLLTIME: %s DEBUGME: %s LOCKLASTS: %s' % (\
		VAR['GRACEPERIOD'],
		VAR['POLLTIME'],
		VAR['DEBUGME'],
		VAR['LOCKLASTS']))
logkpr('Directories: LOGFILE: %s TIMEKPRDIR: %s TIMEKPRWORK: %s TIMEKPRSHARED: %s' % (\
		VAR['LOGFILE'],
		VAR['TIMEKPRDIR'],
		VAR['TIMEKPRWORK'],
		VAR['TIMEKPRSHARED']))

while (True):
	# Check if any accounts should be unlocked and re-activate them
	checklockacct()
	# Check if we have passed midnight, ie new day
	if THISDAY != strftime("%Y%m%d"):
		THISDAY = strftime("%Y%m%d")

	# Get the usernames and PIDs of sessions
	for username in getusers():
		conffile = VAR['TIMEKPRDIR'] + '/' + username
		# Check if user configfile exists and if user was not already notified
		if not isnotified(username):
			logkpr('configuration file for %s exists' % username)
			# Read lists: from, to and limit
			limits, bfrom, bto = readusersettings(username, conffile)
			timefile = VAR['TIMEKPRWORK'] + '/' + username + '.time'
			allowfile = VAR['TIMEKPRWORK'] + '/' + username + '.allow'
			latefile = VAR['TIMEKPRWORK'] + '/' + username + '.late'
			logoutfile = VAR['TIMEKPRWORK'] + '/' + username + '.logout'

			time = int(gettime(timefile, username))
			'''Is the user allowed to be logged in at this time?
			We take it for granted that if they are allowed to login all day ($default_limit) then
			they can login whenever they want, ie they are normal users'''

			# Get current day index and hour of day
			index = int(strftime("%w"))
			hour = int(strftime("%H"))

			logkpr('User: %s Day-Index: %s Seconds-passed: %s' % (username, index, time))

			# Compare: is current hour less than the one in bfrom list?
			if (hour < bfrom[index]):
				logkpr('Current hour less than the defined hour in conffile for user %s' % username)
				if isfile(allowfile):
					if not fromtoday(allowfile):
						logkpr('Extended login hours detected from %s.allow, but not from today' % username)
						threadit(0.5, logOut, username)
						remove(allowfile)
				else:
					# User has not been given extended login hours
					logkpr('Extended hours not detected, %s not in allowed period from-to' %username)
					threadit(0.5, logOut, username)

			# Compare: is current hour greater/equal to $to array?
			if (hour >= bto[index]):
				logkpr('Current hour greater than the defined hour in conffile for user %s' % username)
				# Has the user been given extended login hours?
				if isfile(allowfile):
					if not fromtoday(allowfile):
						logkpr('Extended login hours detected from %s.allow, but not from today' % username)
						# Has the user been late-kicked today?
						if isfile(latefile):
							if fromtoday(latefile):
								logkpr('User %s has been late-kicked today' % username)
								threadit(0.5, logOut, username)
								remove(allowfile)
								#Lock account
								lockacct(username)
							else:
								logkpr('User %s has NOT been late-kicked today' % username)
								threadit(float(VAR['GRACEPERIOD']), logOut, username, latefile)
								threadit(float(VAR['GRACEPERIOD']), remove, allowfile)
								addnotified(username)
								threadit(VAR['GRACEPERIOD'], removenotified, username)
								lockacct(username)
					else:
						logkpr('Extended login hours detected - %s.allow is from today' % username)
				else:
					# User has not been given extended login hours
					logkpr('Extended hours and %s.allow file not detected, %s not in allowed period from-to' % (username, username))
					if isfile(latefile) and fromtoday(latefile):
						logkpr('User %s has been late-kicked today' % username)
						threadit(0.5, logOut, username)
						#Lock account
						lockacct(username)
					else:
						logkpr('User %s has NOT been late-kicked today' % username)
						threadit(float(VAR['GRACEPERIOD']), logOut, username, latefile)
						addnotified(username)
						threadit(VAR['GRACEPERIOD'], removenotified, username)
						lockacct(username)

			# Is the limit exeeded
			# Also includes a fix for a bug that caused an unrestricted user to be kicked and locked at midnight
			if (time > limits[index] and not limits[index] == 86400):
				logkpr('Exceeded today\'s access login duration user %s' % username)
				# Has the user already been kicked out?
				if isfile(logoutfile):
					logkpr('Found %s.logout' % username)
					# Was he kicked out today?
					if fromtoday(logoutfile):
						logkpr('%s has been kicked out today' % username)
						threadit(0.5, logOut, username)
						#Lock account
						lockacct(username)
					else:
						# The user has not been kicked out today
						logkpr('%s has been kicked out, but not today' % username)
						threadit(float(VAR['GRACEPERIOD']), logOut, username, logoutfile)
						addnotified(username)
						threadit(VAR['GRACEPERIOD'], removenotified, username)
						lockacct(username)
				else:
					# The user has not been kicked out before
					logkpr('Not found: %s.logout' % username)
					threadit(float(VAR['GRACEPERIOD']), logOut, username, logoutfile)
					addnotified(username)
					threadit(VAR['GRACEPERIOD'], removenotified, username)
					lockacct(username)

	# Done checking all users, sleeping
	logkpr('Finished checking all users, sleeping for %s seconds' % VAR['POLLTIME'])
	sleep(VAR['POLLTIME'])
