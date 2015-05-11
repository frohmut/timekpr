#!/usr/bin/env python
""" Common variables and definitions for timekpr.
	Copyright / License: See COPYRIGHT.txt
"""

try:
	# python3
	import configparser
except ImportError:
	# python2.x
	import ConfigParser as configparser

from os.path import isfile, getmtime
from os import geteuid
from time import strftime, localtime
from timekprpam import *

def getversion():
	return '0.3.5'

def checkifadmin():
	if geteuid() != 0:
		exit('Error: You need to have administrative privileges to run timekpr')

def getvariables(DEVACTIVE):
	#Read timekpr.conf
	fconf = '/etc/timekpr.conf'
	if DEVACTIVE:
		fconf = './etc/timekpr.conf'
	if not isfile(fconf):
		exit('Error: Could not find configuration file %s' % fconf)

	conf = configparser.ConfigParser()
	try:
		conf.read(fconf)
	except configparser.ParsingError:
		exit('Error: Could not parse the configuration file properly %s' % fconf)

	#Creating a dictionary file
	var = dict()
	#VARIABLES
	#VERSION GRACEPERIOD POLLTIME DEBUGME LOCKLASTS LOGFILE TIMEKPRDIR TIMEKPRWORK TIMEKPRSHARED
	#Exits or sets default if not found

	try:
		var['VERSION'] = conf.get("general", "version")
	except configparser.NoOptionError:
		exit('Error: Could not detect variable version in configuration file %s' % fconf)
	if var['VERSION'] < '0.2.0':
		exit('Error: You have an old /etc/timekpr.conf - remove and reinstall timekpr')

	try:
		var['GRACEPERIOD'] = int(conf.get("variables", "graceperiod"))
	except configparser.NoOptionError:
		var['GRACEPERIOD'] = 120

	try:
		var['POLLTIME'] = int(conf.get("variables", "polltime"))
	except configparser.NoOptionError:
		var['POLLTIME'] = 45

	try:
		var['LOCKLASTS'] = conf.get("variables", "locklasts")
	except configparser.NoOptionError:
		var['LOCKLASTS'] = '1 hour'

	try:
		var['DEBUGME'] = conf.get("variables", "debugme")
	except configparser.NoOptionError:
		var['DEBUGME'] = 'True'

	try:
		var['LOGFILE'] = conf.get("directories", "logfile")
	except configparser.NoOptionError:
		var['LOGFILE'] = '/var/log/timekpr.log'

	try:
		var['TIMEKPRDIR'] = conf.get("directories", "timekprdir")
	except configparser.NoOptionError:
		var['TIMEKPRDIR'] = '/etc/timekpr'

	try:
		var['TIMEKPRWORK'] = conf.get("directories", "timekprwork")
	except configparser.NoOptionError:
		var['TIMEKPRWORK'] = '/var/lib/timekpr'

	try:
		var['TIMEKPRSHARED'] = conf.get("directories", "timekprshared")
	except configparser.NoOptionError:
		var['TIMEKPRSHARED'] = '/usr/share/timekpr'
	if DEVACTIVE:
		var['TIMEKPRSHARED'] = './gui'

	return var

def getcmdoutput(cmd):
	#TODO: timekpr-gui.py: Use it for "/etc/init.d/timekpr status" and a button enable/disable
	from os import popen
	#Execute a command, returns its output
	out = popen(cmd)
	return out.read()

def fromtoday(fname):
	# Returns True if a file was last modified today
	fdate = strftime("%Y%m%d", localtime(getmtime(fname)))
	today = strftime("%Y%m%d")
	return fdate == today

def islate(bto, allowfile):
	# Get current day index and hour of day
	index = int(strftime("%w"))
	hour = int(strftime("%H"))
	if (hour > bto[index]):
		if isfile(allowfile):
			if not fromtoday(allowfile):
				return True
			else:
				return False
		else:
			return True
	else:
		return False

def ispasttime(limits, time):
	index = int(strftime("%w"))
	if (time > limits[index]):
		return True
	else:
		return False

def isearly(bfrom, allowfile):
	# Get current day index and hour of day
	index = int(strftime("%w"))
	hour = int(strftime("%H"))
	if (hour < bfrom[index]):
		if isfile(allowfile):
			if not fromtoday(allowfile):
				return True
			else:
				return False
		else:
			return True
	else:
		return False

def isrestricteduser(username, limit):
	if not isuserlimited(username) and limit == 86400:
		return False
	else:
		return True

def readusersettings(user, conffile):
	#Returns limits and from/to allowed hours
	if isfile(conffile):
		fhandle = open(conffile)
		limits = fhandle.readline() #Read 1st line
		limits = re.compile('(\d+)').findall(limits)
		lims = list(map(int, limits))
	else:
		lims = [ 86400, 86400, 86400, 86400, 86400, 86400, 86400 ]
	bfromandto = getuserlimits(user)
	bfromtemp = bfromandto[0]
	#Using map instead of for i in ...
	bfrom = list(map(int, bfromtemp))

	btotemp = bfromandto[1]
	bto = list(map(int, btotemp))

	return lims, bfrom, bto
