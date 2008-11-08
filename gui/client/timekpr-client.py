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
        self.allowfile = VAR['TIMEKPRWORK'] + '/' + self.username + '.allow'
        self.conffile = '/etc/timekpr/' + self.username
        self.limits, self.bfrom, self.bto = self.readusersettings(self.username, self.conffile)
        self.timer = None
        #Add a gobject loop to check limits:
        self.timer = gobject.timeout_add(self.checkInterval * 1000, self.checkLimits)
        #Add a notifier every 15 minutes
        self.pn = gobject.timeout_add(15 * 60 * 1000, self.pnotifier)

    def fractSec(s):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def gettime(self, tfile):
        t = open(tfile)
        time = int(t.readline())
        t.close()
        return time
    
    def get_de():
        '''
        Detect desktop environment
        '''
    
        if os.environ.has_key("KDE_FULL_SESSION") or os.environ.has_key("KDE_MULTIHEAD"):
            return "KDE"
        elif os.environ.has_key("GNOME_DESKTOP_SESSION_ID") or os.environ.has_key("GNOME_KEYRING_SOCKET"):
            return "GNOME"
        elif getcmdoutput("xprop -root _DT_SAVE_MODE").strip().endswith(' = "xfce4"'):
            return "XFCE"


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
        time = self.gettime(self.timefile)
        if isearly(self.bfrom, self.allowfile):
            self.notifier('You are early.')
        
        if islate(self.bto, self.allowfile):
            self.notifier('You are late.')
        
        if ispasttime(self.limits, time):
            self.notifier('Your time is up')
	return True

    def pnotifier(self):
        time = self.gettime(self.timefile)
        index = int(strftime("%w"))
        left = self.limits[index] - time
        h, m, s = self.fractSec(left)
        self.notifier('You have %s hour(s), %s minute(s) and %s seconds left' % (h, m, s))
        
        # if time left is less than 15 minutes, notify every 5 minutes
        if time < 900:
            self.pn = gobject.timeout_add(5 * 60 * 1000, self.pnotifier)
        
        # if time left is less than 5 minutes, notify every minute
        if time < 300:
            self.pn = gobject.timeout_add(1 * 60 * 1000, self.pnotifier)
        return True

    def notifier(self, message):
        if self.get_de() == 'GNOME' or self.get_de() == 'XFCE':
            getcmdoutput('notify-send --icon=gtk-dialog-warning --urgency=critical -t 2000 "' + title + '" "' + message + '"')
        else:
            getcmdoutput('dcop knotify default notify notifying timekpr-client "' + message + '" "" "" 16 0')
    
    def main(self):
        gtk.main()

#Start
if __name__ == "__main__":
    tc = TimekprClient()
    tc.main()