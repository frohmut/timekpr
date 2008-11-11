#!/usr/bin/env python
""" Common variables and definitions for timekpr.
    Copyright / License: See COPYRIGHT.txt
"""

import ConfigParser
from os.path import isfile, getmtime
from os import geteuid
from time import strftime, localtime

def getversion(): 
    return '0.2.2'

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
    
    conf = ConfigParser.ConfigParser()
    try:
        conf.read(fconf)
    except ConfigParser.ParsingError:
        exit('Error: Could not parse the configuration file properly %s' % fconf)
    
    #Creating a dictionary file
    var = dict()
    #VARIABLES
    #VERSION GRACEPERIOD POLLTIME DEBUGME LOCKLASTS LOGFILE TIMEKPRDIR TIMEKPRWORK TIMEKPRSHARED
    #Exits or sets default if not found
    
    try:
        var['VERSION'] = conf.get("general", "version")
    except ConfigParser.NoOptionError:
        exit('Error: Could not detect variable version in configuration file %s' % fconf)
    if var['VERSION'] < '0.2.0':
        exit('Error: You have an old /etc/timekpr.conf - remove and reinstall timekpr')
    
    try:
        var['GRACEPERIOD'] = int(conf.get("variables", "graceperiod"))
    except ConfigParser.NoOptionError:
        var['GRACEPERIOD'] = 120
    
    try:
        var['POLLTIME'] = int(conf.get("variables", "polltime"))
    except ConfigParser.NoOptionError:
        var['POLLTIME'] = 45
    
    try:
        var['LOCKLASTS'] = conf.get("variables", "locklasts")
    except ConfigParser.NoOptionError:
        var['LOCKLASTS'] = '1 hour'
    
    try:
        var['DEBUGME'] = conf.get("variables", "debugme")
    except ConfigParser.NoOptionError:
        var['DEBUGME'] = 'True'
    
    try:
        var['LOGFILE'] = conf.get("directories", "logfile")
    except ConfigParser.NoOptionError:
        var['LOGFILE'] = '/var/log/timekpr.log'
    
    try:
        var['TIMEKPRDIR'] = conf.get("directories", "timekprdir")
    except ConfigParser.NoOptionError:
        var['TIMEKPRDIR'] = '/etc/timekpr'
    
    try:
        var['TIMEKPRWORK'] = conf.get("directories", "timekprwork")
    except ConfigParser.NoOptionError:
        var['TIMEKPRWORK'] = '/var/lib/timekpr'
    
    try:
        var['TIMEKPRSHARED'] = conf.get("directories", "timekprshared")
    except ConfigParser.NoOptionError:
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

