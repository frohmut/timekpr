#!/usr/bin/env python
import os.path, os mkdir

# Copyright / License:
# Copyright (c) 2008 Chris Jackson <chris@91courtstreet.net>
# Further developed by Even Nedberg <code@nedberg.net> and Savvas Radevic <vicedar@gmail.com>
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
grace_period = 120

# How often should the script check the timelogs.
# Setting is expressed in seconds, e.g. 45 means 45 seconds.
poll_time = 45

#Create a log?
DEBUGME = True
LOGF = '/var/log/timekpr.log'

#Default lock period
#Setting can be day(s), hour(s), minute(s)
#Example: 5 hours
lock_lasts = "1 hour"

## CONFIGURE END - Do not edit after this line!

#To log: logkpr "Something" >> $LOGF

#Default directory
TIMEKPRDIR = '/etc/timekpr'

#TO-DO
#Check if it exists, if not, create it
if not os.path.isdir(TIMEKPRDIR):
	os.mkdir(TIMEKPRDIR)

#Ubuntu uses alternatives so we look for x-session-manager instead of gnome-session
SESSION_MANAGER = 'x-session-manager'

def logkpr(string):
	

def notify(user, message):
	

def logOut(user):
	

def lockaact(user):
	

def checklockacct():
	

while (True):
	

