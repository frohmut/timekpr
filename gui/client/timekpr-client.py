#!/usr/bin/env python

import gtk
import gobject
import os
from time import strftime, sleep
from timekprpam import *
from timekprcommon import *

class TimekprClient:
    def __init__(self):
        self.VAR = getvariables(False)
        self.checkInterval = 60
        self.tray = gtk.StatusIcon()
        self.red = self.VAR['TIMEKPRSHARED'] + '/timekpr32x32.png'
        self.tray.set_from_file(self.red)
        self.tray.set_tooltip('Timekpr-client')
        self.tray.set_visible(True)
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.username = os.getenv('USER')
        self.timefile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.time'
        self.allowfile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.allow'
        self.conffile = '/etc/timekpr/' + self.username
        self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)
        self.timer = None
        #Add a gobject loop to check limits:
        self.timer = gobject.timeout_add(self.checkInterval * 1000, self.checkLimits)
        #Add a notifier every 15 minutes
        gobject.timeout_add(15 * 60 * 1000, self.pnotifier)

    def fractSec(self, s):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def gettime(self, tfile):
        t = open(tfile)
        time = int(t.readline())
        t.close()
        return time
    
    def now():
        return datetime.datetime.now()
    
    def timeofbto():
        return datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day, self.bto, 0, 0)
    
    def get_de(self):
        '''
        Detect desktop environment
        '''
        if os.environ.has_key("KDE_FULL_SESSION") or os.environ.has_key("KDE_MULTIHEAD"):
            return "KDE"
        elif os.environ.has_key("GNOME_DESKTOP_SESSION_ID") or os.environ.has_key("GNOME_KEYRING_SOCKET"):
            return "GNOME"
        elif getcmdoutput("xprop -root _DT_SAVE_MODE").strip().endswith(' = "xfce4"'):
            return "XFCE"

    def kde_version(self):
        version = getcmdoutput('echo $KDE_SESSION_VERSION')
        if version == "\n":
            return 3
        else:
            return int(version)

    '''
    Left click
    '''
    def on_activate(self, data):
        self.pnotifier()

    '''
    Right click
    '''
    def on_popup_menu(self, status, button, time):
        self.pnotifier()

    '''
    Run every checkInterval seconds, check if user has run out of time
    '''
    def checkLimits(self):
        # Re-read settings in case they changed
        self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)
        
        # In case timefile does not exist yet
        if not self.gettime(self.timefile):
            return True
        
        time = self.gettime(self.timefile)
        if isearly(self.bfrom, self.allowfile):
            self.notifier('You are early, you will be logged out in LESS than 2 minutes')
        
        if islate(self.bto, self.allowfile):
            self.notifier('You are late, you will be logged out in LESS than 2 minutes')
        
        if ispasttime(self.limits, time):
            self.notifier('Your time is up, you will be logged out in LESS than 2 minutes')
	return True
    
    def timeleftstring(self, h, m, s):
        if h > 1 or h == 0:
            if m > 1 or m == 0:
                message = 'You have %s hours, %s minutes and %s seconds left' % (h, m, s)
            else:
                message = 'You have %s hours, %s minute and %s seconds left' % (h, m, s)
        else:
            if m > 1 or m == 0:
                message = 'You have %s hour, %s minutes and %s seconds left' % (h, m, s)
            else:
                message = 'You have %s hour, %s minute and %s seconds left' % (h, m, s)
        
        return message

    def pnotifier(self):
        if not self.gettime(self.timefile):
            return True
        
        index = int(strftime("%w"))
        
        # How much time if left?
        usedtime = self.gettime(self.timefile)
        timeleft = self.limits[index] - usedtime
        timeuntil = self.timeofbto() - self.now()
        
        if timeleft <= timeuntil:
            left = timeleft
        else:
            left = timeuntil
        
        if left <= 0:
            self.notifier('Your time is up, you will be logged out in less than 2 minutes')
            return True
        h, m, s = self.fractSec(left)
        message = self.timeleftstring(h, m, s)
        self.notifier(message)
        
        # if time left is less than 5 minutes, notify every minute
        if time < 300:
            gobject.timeout_add(1 * 60 * 1000, self.pnotifier)
            return False
        
        # if time left is less than 15 minutes, notify every 5 minutes
        if time < 900:
            gobject.timeout_add(5 * 60 * 1000, self.pnotifier)
            return False

        return True

    def notifier(self, message):
        title = "Timekpr"
        if self.get_de() == 'GNOME' or self.get_de() == 'XFCE':
            getcmdoutput('notify-send --icon=gtk-dialog-warning --urgency=critical -t 3000 "' + title + '" "' + message + '"')
        else:
            if self.kde_version() == 4:
                import sys
                import dbus
                kn = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
                i = kn.event("warning", "kde", [], message, [0,0,0,0], [], 0, dbus_interface="org.kde.KNotify")
                sleep(10)
                kn.closeNotification(i)
            else:
                getcmdoutput('dcop knotify default notify notifying timekpr-client "' + message + '" "" "" 16 0')
    
    def main(self):
        gtk.main()

#Start
if __name__ == "__main__":
    tc = TimekprClient()
    tc.main()
