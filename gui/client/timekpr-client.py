#!/usr/bin/env python

import gtk
import gobject
import os
from time import strftime
from timekprpam import *
from timekprcommon import *

class TimekprClient:
    def __init__(self):
        VAR = getvariables(False)
        self.checkInterval = 5
        self.tray = gtk.StatusIcon()
        self.tray.set_from_file("../timekpr32x32.png")
        self.tray.set_tooltip('Timekpr-client')
        self.tray.set_visible(True)
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.username = os.getenv('USER')
        self.timefile = VAR['TIMEKPRWORK'] + '/' + self.username + '.time'
        self.conffile = '/etc/timekpr/' + self.username
        self.limits, self.bfrom, self.bto = self.readusersettings(self.username, self.conffile)
        self.timer = None
        #Add a gobject loop to check limits:
        self.timer = gobject.timeout_add(self.checkInterval * 1000, self.checkLimits)


    def gettime(self, tfile):
        t = open(tfile)
        time = int(t.readline())
        t.close()
        return time


    '''
    Copied from timekpr.py, should this be placed in timekprcommon.py?
    '''
    def readusersettings(self, user, conffile):
        #Returns limits and from/to allowed hours
        fhandle = open(conffile)
        limits = fhandle.readline() #Read 1st line

        bfromandto = getuserlimits(user)
        bfromtemp = bfromandto[0]
        #Using map instead of for i in ...
        bfrom = map(int, bfromtemp)

        btotemp = bfromandto[1]
        bto = map(int, btotemp)

        limits = re.compile('(\d+)').findall(limits)
        lims = map(int, limits)

        return lims, bfrom, bto

    '''
    Left click
    
    We can use this to display the time left
    '''
    def on_activate(self, data):
        print 'active'

    '''
    Right click
    
    Not sure if we will need this
    Perhaps a menu that can be used to request extra time? How could we do that?
    '''
    def on_popup_menu(self, status, button, time):
        print 'popup menu'

    '''
    Run every checkInterval seconds, check if user has run out of time
    '''
    def checkLimits(self):
        print 'Check limits'
        self.notifier('notify-send --icon=gtk-dialog-warning --urgency=critical -t 2000 title message')
        index = int(strftime("%w"))
        time = self.gettime(self.timefile)
        print time
        print self.limits[index]
        print self.bfrom[index]
        print self.bto[index]
	return True

    def notifier(self, cmd):
        getcmdoutput(cmd)
    
    def main(self):
        gtk.main()

#Start
if __name__ == "__main__":
    tc = TimekprClient()
    tc.main()