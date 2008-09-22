#!/usr/bin/env python
import os.path, os mkdir, getpass, re

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

#Default configuration file
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

#Read configuration file TIMEKPRCONF (use re module)
def readconf(conffile):
	

#Ubuntu uses alternatives so we look for x-session-manager instead of gnome-session
SESSION_MANAGER = 'x-session-manager'

#To log: logkpr "Something" >> $LOGF
def logkpr(string):
	

def notify(user, message):
	

def logOut(user):
	

def lockaact(user):
	

def checklockacct():
	

while (True):
	

