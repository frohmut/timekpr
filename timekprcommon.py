#!/usr/bin/env python
# Copyright / License: See debian/copyright
def getversion(): return '0.2.0'

def checkifadmin():
	from getpass import getuser
	if getuser() != "root": exit('Error: You do not have administrative privileges')

def getvariables(DEVACTIVE):
	from os.path import isfile
	#Read timekpr.conf
	fconf = '/etc/timekpr.conf'
	if DEVACTIVE: fconf = './etc/timekpr.conf'
	if not isfile(fconf): exit('Error: Could not find configuration file %s' % fconf)
	
	import ConfigParser
	conf = ConfigParser.ConfigParser()
	try: conf.read(fconf)
	except ConfigParser.ParsingError: exit('Error: Could not parse the configuration file properly %s' % fconf)
	
	#Creating a dictionary file
	var = dict()
	#VARIABLES
	#VERSION GRACEPERIOD POLLTIME DEBUGME LOCKLASTS LOGFILE TIMEKPRDIR TIMEKPRWORK TIMEKPRSHARED
	#Exits or sets default if not found
	
	try: var['VERSION'] = conf.get("general","version")
	except ConfigParser.NoOptionError: exit('Error: Could not detect variable version in configuration file %s' % fconf)
	if var['VERSION'] < '0.2.0': exit('Error: You have an old /etc/timekpr.conf - remove and reinstall timekpr')
	
	try: var['GRACEPERIOD'] = int(conf.get("variables","graceperiod"))
	except ConfigParser.NoOptionError: var['GRACEPERIOD'] = 120
	
	try: var['POLLTIME'] = int(conf.get("variables","polltime"))
	except ConfigParser.NoOptionError: var['POLLTIME'] = 45
	
	try: var['LOCKLASTS'] = conf.get("variables","locklasts")
	except ConfigParser.NoOptionError: var['LOCKLASTS'] = '1 hour'
	
	try: var['DEBUGME'] = conf.get("variables","debugme")
	except ConfigParser.NoOptionError: var['DEBUGME'] = 'True'
	
	try: var['LOGFILE'] = conf.get("directories","logfile")
	except ConfigParser.NoOptionError: var['LOGFILE'] = '/var/log/timekpr.log'
	
	try: var['TIMEKPRDIR'] = conf.get("directories","timekprdir")
	except ConfigParser.NoOptionError: var['TIMEKPRDIR'] = '/etc/timekpr'
	
	try: var['TIMEKPRWORK'] = conf.get("directories","timekprwork")
	except ConfigParser.NoOptionError: var['TIMEKPRWORK'] = '/var/lib/timekpr'
	
	try: var['TIMEKPRSHARED'] = conf.get("directories","timekprshared")
	except ConfigParser.NoOptionError: var['TIMEKPRSHARED'] = '/usr/share/timekpr'
	if DEVACTIVE: var['TIMEKPRSHARED'] = './gui'
	
	return var

def getcmdoutput(cmd):
	from os import popen
	#Execute a command, returns its output
	out = popen(cmd)
	return out.read()
