#!/usr/bin/env python
""" Common variables and definitions for timekpr."""

#    Copyright (C) 2008-2009 Savvas Radevic <vicedar@gmail.com>
#    Copyright (C) 2008-2009 Even Nedberg <even@nedberg.net>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

try:
    # python2.x
    import ConfigParser as configparser
except ImportError:
    # python3
    import configparser

from os.path import isfile, getmtime
from os import geteuid
from time import strftime, localtime
from timekprpam import *

def getversion():
    return '0.3.0'

def checkifadmin():
    if geteuid() != 0:
        exit('Error: You need to have administrative privileges to run timekpr')

# GRACEPERIOD:
# This is the grace period, where a notification pops up letting the users
# know that their time usage will be over soon.
# Users are given by default 120 seconds to finish up their work.
# Limit is expressed in seconds, e.g. 120 means 2 minutes
# POLLTIME: How often should the script check the timelogs.
# Setting is expressed in seconds, e.g. 45 means 45 seconds.
# DEBUGME: True keeps a logfile, False does not.
# LOCKLASTS: Default lock period
# Setting can be day(s), hour(s), minute(s), month(s) (30 days)
# Example: 5 hours

GRACEPERIOD = 120
POLLTIME = 45
DEBUGME = True
LOCKLASTS = '1 hour'

#TODO: Change it, fix it, make it work.
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
