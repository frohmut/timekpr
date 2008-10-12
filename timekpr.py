#!/usr/bin/env python
# Copyright / License: See debian/copyright

import re, sys
from getpass import getuser
from time import strftime, sleep, localtime, mktime, time
from os.path import split as splitpath, isfile, isdir, getmtime
from os import popen, mkdir, kill, remove
from glob import glob

#If DEVACTIVE is true, it uses files from local directory
DEVACTIVE = True

#Read timekpr.conf
TIMEKPRCONF = '/etc/timekpr.conf'
if DEVACTIVE: TIMEKPRCONF = './timekpr.conf'

if not isfile(TIMEKPRCONF): exit('Could not find configuration file '+TIMEKPRCONF)
import ConfigParser
conf = ConfigParser.ConfigParser()
try: conf.read(TIMEKPRCONF)
except ConfigParser.ParsingError: exit('Could not parse the configuration file properly '+TIMEKPRCONF)

#Importing variables GRACEPERIOD POLLTIME DEBUGME LOCKLASTS LOGFILE TIMEKPRDIR TIMEKPRWORK TIMEKPRSHARED
#Sets default if not found
try: GRACEPERIOD = int(conf.get("variables","graceperiod"))
except ConfigParser.NoOptionError: GRACEPERIOD = 120

try: POLLTIME = int(conf.get("variables","polltime"))
except ConfigParser.NoOptionError: POLLTIME = 45

try: LOCKLASTS = conf.get("variables","locklasts")
except ConfigParser.NoOptionError: LOCKLASTS = '1 hour'

try: DEBUGME = conf.get("variables","debugme")
except ConfigParser.NoOptionError: DEBUGME = 'True'

try: LOGFILE = conf.get("directories","logfile")
except ConfigParser.NoOptionError: LOGFILE = '/var/log/timekpr.log'

try: TIMEKPRDIR = conf.get("directories","timekprdir")
except ConfigParser.NoOptionError: TIMEKPRDIR = '/etc/timekpr'

try: TIMEKPRWORK = conf.get("directories","timekprwork")
except ConfigParser.NoOptionError: TIMEKPRWORK = '/var/lib/timekpr'

#Import modules
try: TIMEKPRSHARED = conf.get("directories","timekprshared")
except ConfigParser.NoOptionError: TIMEKPRSHARED = '/usr/share/timekpr'

if DEVACTIVE: TIMEKPRSHARED = '.'
sys.path.append(TIMEKPRSHARED)
from timekprpam import * # timekprpam.py

#Check if admin
if getuser() != "root": exit('Error: You do not have administrative privileges')

#Check if it exists, if not, create it
if not isdir(TIMEKPRDIR): mkdir(TIMEKPRDIR)
if not isdir(TIMEKPRWORK): mkdir(TIMEKPRWORK)

# Lists keeping track of users who has been latekicked or loggedout
latekickedusers = list()
loggedoutusers = list()

# Keep track of todays date
THISDAY = strftime("%Y%m%d", localtime())

#Ubuntu uses alternatives so we look for x-session-manager instead of gnome-session
SESSION_MANAGER = 'x-session-manager'

def logkpr(string,clear=0):
	#To log: logkpr("Something")
	#To clear file and log: logkpr("Something",1)
	if DEBUGME != 'True': return
	if clear == 1:
		l = open(LOGFILE, 'w')
	else:
		l = open(LOGFILE, 'a')
	nowtime = strftime('%Y-%m-%d %H:%M:%S ', localtime())
	l.write(nowtime + string +'\n')

def logOut(user,pid):
	#Forces the user to log out.
	if issessionalive(user):
		logkpr('logOut: Attempting killing '+user+' (TERM, 15)...')
		#this is a pretty bad way of killing a gnome-session, but we warned 'em
		pid = int(pid)
		kill(pid,15)
		sleep(5)
		if issessionalive(user):
			logkpr('logOut: Process still there, attempting force-killing '+user+' (KILL, 9)...')
			kill(pid,9)
		#logkpr('logOut: touched $username.logout')
		#touched?
	
	''' uncomment the following to brutally kill all of the users processes
		sleep 5
		pkill -u $username
	# killing gnome-session should be more like:
	DISPLAY=":0" XAUTHORITY="/tmp/.gdmEQ0V5T" SESSION_MANAGER="local/wretched:/tmp/.ICE-unix/$pid" su -c 'gnome-session-save --kill --silent' $username
	# but this can still leave processes to cleanup - plus it's not easy to get SESSION_MANAG
	'''

## Using Linux-PAM to lock and disable users
def getlocklasts():
	#Returns the LOCKLASTS variable in seconds
	t=re.compile('(\d+) (second|minute|hour|day|week|month|year)s?').match(LOCKLASTS)
	if not t: exit('Error: LOCKLASTS is badly formatted, should be something like "1 week" or "2 hours"')
	#n = time length
	#m = second|minute|hour|day|week|month|year
	(n,m)=(int(t.group(1)),t.group(2))
	#variable dictionary: multiply
	multiply = {
		'second': n,
		'minute': n*60,
		'hour': n*60*60,
		'day': n*60*60*24,
		'week': n*60*60*24*7,
		'month': n*60*60*24*30
	}
	#Return in seconds (integer)
	return multiply[m]

def lockacct(u):
	#Locks user and sets the date in a file
	logkpr('lockacct called with user: ' + u)
	lockfile = TIMEKPRDIR + '/' + u + '.lock'
	f = open(lockfile, 'w')
	f.close()
	lockuser(u) # timekprpam.py

def checklockacct():
	#Check if user should be unlocked and unlock them
	logkpr('checklockacct called')
	#Find *.lock in TIMEKPRDIR
	s = TIMEKPRDIR + '/' + '*.lock'
	l = glob(s)
	for f in l:
		#Get username from filename - os.path.split
		u = splitpath(f)[1].replace('.lock','')
		lastmodified = getmtime(f) #Get last modified time from username.lock file
		#Get time when lock should be lifted
		dtlock = lastmodified + getlocklasts()
		dtnow = time()
		#If time now is great than or equal to the time when lock should be lifted
		if dtnow >= dtlock:
			logkpr('checklockacct: ' + u + ' should be unlocked, unlocking..')
			unlockuser(u)
			logkpr('checklockacct: removing ' + u + '.lock file..')
			remove(f)

## File defs
def fileisok(fname):
	#File exists and is today's?
	if isfile(fname) and fromtoday(fname): return True
	return False

def readusersettings(user, conffile):
	#Returns limits and from/to allowed hours
	fhandle = open(conffile)
	limits = fhandle.readline() #Read 1st line
	#bfrom = list()
	#bto = list()
	#lims = list()
	bfromandto = getuserlimits(user)
	bfromtemp = bfromandto[0]
	#Using map instead of for i in ...
	bfrom = map(int,bfromtemp)
	#for i in range(len(bfromtemp)):
	#	bfrom.append(int(bfromtemp[i]))
	btotemp = bfromandto[1]
	bto = map(int,btotemp)
	#for i in range(len(btotemp)):
	#	bto.append(int(btotemp[i]))
	limits = re.compile('(\d+)').findall(limits)
	lims = map(int,limits)
	#for i in range(len(limits)):
	#	lims.append(int(limits[i]))
	return lims, bfrom, bto

def getcmdoutput(cmd):
	#Execute a command, returns its output
	out = popen(cmd)
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
	# Returns:	True if process is still there (user logged in),
	#		False if user has logged out
	for u,p in getsessions():
		if u == user: return True
	return False

def getdbus(pid):
	#Returns DBUS_SESSION_BUS_ADDRESS variable from /proc/pid/environ
	pid = str(pid)
	p = open('/proc/'+pid+'/environ', 'r').read()
	i = re.compile('(DBUS_SESSION_BUS_ADDRESS=[^\x00]+)').search(p)
	return i.group(1)
	pass
	#Returns: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7
	#Note:	If you would use [^,] in regex you would get: DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw

def notify(user, pid, title, message):
	'''
	Sends a notification via notify-send
	Usage: notify( "youruser", "pid", "your title", "your message")
	We will be probably using pynotify module for this, we'll see!
	'''
	#If the user has logged out, don't notify
	if issessionalive(user) is False:
		logkpr('notify called but cancelled, could not find alive session of '+user)
		return
	logkpr('notify called for '+user)
	
	#WARNING: Don't use the exclamation mark ("!") in the message or title, otherwise bash will return something like: -bash: !": event not found
	#Might be good to include these substitutions, if someone doesn't read this warning
	title = re.compile('!').sub('\!', title)
	message = re.compile('!').sub('\!', message)
	#Get DBus
	dbus = getdbus(pid)
	#Create and send command
	notifycmd = 'su %s -c "%s notify-send --icon=gtk-dialog-warning --urgency=critical -t 10000 \\"%s\\" \\"%s\\""' % (user, dbus, title, message)
	reply = getcmdoutput(notifycmd)
	logkpr('notify command for '+user+': '+notifycmd)
	
	'''The long representations in terminal:
	# su username -c "DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send \"title\" \"message\""
	# sudo -u username DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-qwKxIfaWLw,guid=7215562baaa1153521197dc648d7bce7 notify-send "title" "message"
	'''

def gettime(tfile):
	#Adds time to the timefile
	if fileisok(tfile):
		logkpr('This day\'s ' + username + '.time file exists, adding time')
		t = open(tfile)
		newtime = int(t.readline()) + POLLTIME
	else:
		t = open(tfile, 'w')
		newtime = POLLTIME
	t.close()
	writetime(tfile, newtime)
	return newtime

def writetime(tfile, time):
	#Write time to timefile
	f = open(tfile, 'w')
	f.write(str(time))

def islatekicked(user):
	# Returns True if the user has been latekicked today
	return user in latekickedusers

def isloggedout(user):
	# Returns True if the user has been logged out earlier today
	return user in loggedoutusers

def latekick(user):
	# Adds a user to the latekickedusers list
	if not islatekicked(user):
		latekickedusers.append(user)

def loggedout(user):
	# Adds a user to the loggedoutusers list
	if not isloggedout(user):
		loggedoutusers.append(user)

def fromtoday(fname):
	# Returns True if a file was last modified today
	fdate = strftime("%Y%m%d", localtime(getmtime(fname)))
	today = strftime("%Y%m%d", localtime())
	return fdate == today

logkpr('Starting timekpr',1)
logkpr('Variables: '+str(GRACEPERIOD)+' '+str(POLLTIME)+' '+DEBUGME+' '+LOCKLASTS)
logkpr('Directories: '+LOGFILE+' '+TIMEKPRDIR+' '+TIMEKPRWORK+' '+TIMEKPRSHARED)

while (True):
	# Check if any accounts should be unlocked and re-activate them
	checklockacct()
	# Check if we have passed midnight, ie new day
	if THISDAY != strftime("%Y%m%d", localtime()):
		logkpr('New day, resetting loggedoutusers and latekickedusers.')
		del latekickedusers[:]
		del loggedoutusers[:]
		THISDAY = strftime("%Y%m%d", localtime())
	
	# Get the usernames and PIDs of sessions
	for username, pid in getsessions():
		conffile = TIMEKPRDIR + '/' + username
		# Check if user configfile exists, if it doesn't the user is unrestricted and we need not check any more
		if isfile(conffile):
			logkpr('conffile of ' + username + ' exists')
			# Read lists: from, to and limit
			limits, bfrom, bto = readusersettings(username, conffile)
			timefile = TIMEKPRWORK + '/' + username + '.time'
			allowfile = TIMEKPRWORK + '/' + username + '.allow'
			latefile = TIMEKPRWORK + '/' + username + '.late'
			logoutfile = TIMEKPRWORK + '/' + username + '.logout'
			
			time = int(gettime(timefile))
			'''Is the user allowed to be logged in at this time?
			We take it for granted that if they are allowed to login all day ($default_limit) then
			they can login whenever they want, ie they are normal users'''
			
			# Get current day index and hour of day
			index = int(strftime("%w", localtime()))
			hour = int(strftime("%H", localtime()))
			
			logkpr('User ' + username + ' PID ' + str(pid) + ' Day-Index: ' + str(index) + ' Seconds-passed: ' + str(time))
			
			# Compare: is current hour less than the one in bfrom list?
			if (hour < bfrom[index]):
				logkpr('Current hour less than the defined hour in conffile for user: ' + username)
				if isfile(allowfile):
					if not fromtoday(allowfile):
						logkpr('Extended login hours detected from ' + username + '.allow, but not from today')
						logOut(username, pid)
						remove(allowfile)
				else:
					# User has not been given extended login hours
					logkpr('Extended hours not detected, ' + username + ' not in allowed period from-to')
					logOut(username, pid)
			
			# Compare: is current hour greater/equal to $to array?
			if (hour > bto[index]):
				logkpr('Current hour greater than the defined hour in conffile for user: ' + username)
				# Has the user been given extended login hours?
				if isfile(allowfile):
					if not fromtoday(allowfile):
						logkpr('Extended login hours detected from ' + username + '.allow, but not from today')
						# Has the user been late-kicked today?
						if isfile(latefile):
							if fromtoday(latefile):
								logkpr('User: ' + username + ' has been late-kicked today')
								logOut(username, pid)
								remove(allowfile)
								#Lock account
								lockacct(username)
							else:
								logkpr('User: ' + username + ' has NOT been late-kicked today')
								notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + str(bfrom[index]) + ' and ' + str(bto[index]) + '.  You will be logged out in ' + str(GRACEPERIOD) + ' seconds.')
								sleep(GRACEPERIOD/2)
								notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + str(bfrom[index]) + ' and ' + str(bto[index]) + '.  You will be logged out in ' + str(GRACEPERIOD/2) + ' seconds.')
								sleep(GRACEPERIOD/2)
								open(latefile, 'w')
								remove(allowfile)
					else:
						logkpr('Extended login hours detected ' + username + '.allow is from today')
				else:
					# User has not been given extended login hours
					logkpr('Extended hours not detected, ' + username + ' not in allowed period from-to')
					if isfile(latefile) and fromtoday(latefile):
						logkpr('User: ' + username + ' has been late-kicked today')
						logOut(username, pid)
						#Lock account
						lockacct(username)
					else:
						logkpr('User: ' + username + ' has NOT been late-kicked today')
						notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + str(bfrom[index]) + ' and ' + str(bto[index]) + '.  You will be logged out in ' + str(GRACEPERIOD) + ' seconds.')
						sleep(GRACEPERIOD/2)
						notify(username, pid, 'It is getting late', 'You are only allowed to login between ' + str(bfrom[index]) + ' and ' + str(bto[index]) + '.  You will be logged out in ' + str(GRACEPERIOD/2) + ' seconds.')
						sleep(GRACEPERIOD/2)
						logOut(username, pid)
						open(latefile, 'w')
			
			# Is the limit exeeded
			if (time > limits[index]):
				logkpr('Exceeded today\'s access duration, user: ' + username)
				# Has the user already been kicked out?
				if isfile(logoutfile):
					logkpr('Found: ' + username + '.logout')
					# Was he kicked out today?
					if fromtoday(logoutfile):
						logkpr(username + ' has been kicked out today')
						logOut(username, pid)
						#Lock account
						lockacct(username)
					else:
						# The user has not been kicked out today
						logkpr(username + ' has been kicked out, but not today')
						notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit. You will be logged out in ' + str(GRACEPERIOD) + ' seconds.')
						sleep(GRACEPERIOD/2)
						notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit. You will be logged out in ' + str(GRACEPERIOD/2) + ' seconds.')
						sleep(GRACEPERIOD/2)
						logOut(username, pid)
						open(logoutfile, 'w')
				else:
					# The user has not been kicked out before
					logkpr('Not found: ' + username + '.logout')
					notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit. You will be logged out in ' + str(GRACEPERIOD) + ' seconds')
					sleep(GRACEPERIOD/2)
					notify(username, pid, 'Passed limit', 'You have exeeded your daily time limit. You will be logged out in ' + str(GRACEPERIOD/2) + ' seconds')
					sleep(GRACEPERIOD/2)
					logOut(username, pid)
					open(logoutfile, 'w')
	
	# Done checking all users, sleeping
	logkpr('Finished checking all users, sleeping for ' + str(POLLTIME) + ' seconds')
	sleep(POLLTIME)
