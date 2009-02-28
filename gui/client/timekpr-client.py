#!/usr/bin/env python

import gtk
import gobject
import os
from time import strftime, sleep
import datetime
from timekprpam import *
from timekprcommon import *

import locale
import gettext
import sys

APP_NAME = "timekpr"

#Translation stuff
#Get the local directory
local_path = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, local_path)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

class TimekprClient:
    def __init__(self):
        self.VAR = getvariables(False)
        self.checkInterval = 60
        self.tray = gtk.StatusIcon()
        self.red = self.VAR['TIMEKPRSHARED'] + '/timekpr32x32.png'
        self.green = self.VAR['TIMEKPRSHARED'] + '/padlock-green.png'
        self.tray.set_from_file(self.red)
        self.tray.set_tooltip('Timekpr-client')
        self.tray.set_visible(True)
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.username = os.getenv('USER')
        self.timefile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.time'
        self.allowfile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.allow'
        self.conffile = self.VAR['TIMEKPRDIR'] + self.username
        self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)
        self.timer = None
        self.checkLimits()
        #Add a gobject loop to check limits:
        self.timer = gobject.timeout_add(self.checkInterval * 1000, self.checkLimits)
        #Add a notifier every 15 minutes
        gobject.timeout_add(15 * 60 * 1000, self.pnotifier)

    def fractSec(self, s):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return h, m, s

    '''
    Returns the number of seconds a user has left, False if user.time does not exist
    '''
    def gettime(self, tfile):
        if not isfile(tfile):
            return False
        t = open(tfile)
        time = int(t.readline())
        t.close()
        return time

    '''
    Returns current time
    '''
    def now(self):
        return datetime.datetime.now()

    def timeofbto(self, index):
        y = datetime.date.today().year
        m = datetime.date.today().month
        d = datetime.date.today().day
        h = self.bto[index]
        date = datetime.date(y, m, d)
        if h == 24:
            h = 0
            date = date + datetime.timedelta(days=1)
        dt = datetime.datetime(date.year, date.month, date.day, h, 0, 0)
        return dt

    '''
    Detect and return the desktop environment user is using
    '''
    def get_de(self):
        if os.environ.has_key("KDE_FULL_SESSION") or os.environ.has_key("KDE_MULTIHEAD"):
            return "KDE"
        elif os.environ.has_key("GNOME_DESKTOP_SESSION_ID") or os.environ.has_key("GNOME_KEYRING_SOCKET"):
            return "GNOME"
        elif getcmdoutput("xprop -root _DT_SAVE_MODE").strip().endswith(' = "xfce4"'):
            return "XFCE"

    '''
    Returns the version of KDE in use (4 if KDE4, or 3 for everything else)
    '''
    def kde_version(self):
        version = getcmdoutput('echo $KDE_SESSION_VERSION')
        if version == "\n":
            return 3
        else:
            return int(version)

    '''
    Left click on tray icon
    '''
    def on_activate(self, data):
        self.pnotifier()

    '''
    Right click on tray icon
    Should we add a menu to this action?
    '''
    def on_popup_menu(self, status, button, time):
        self.pnotifier()

    '''
    Run every checkInterval seconds, check if user has run out of time
    '''
    def checkLimits(self):
        # Re-read settings in case they changed
        self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)

        index = int(strftime("%w"))
        # If the user is not a restricted user, set the tray icon to green padlock
        if not isrestricteduser(self.username, self.limits[index]):
            self.tray.set_from_file(self.green)
            return
        else:
            self.tray.set_from_file(self.red)

        # In case timefile does not exist yet
        if not self.gettime(self.timefile):
            return True

        time = self.gettime(self.timefile)
        if isearly(self.bfrom, self.allowfile):
            self.notifier(_('You are early, you will be logged out in LESS than 2 minutes'))

        if islate(self.bto, self.allowfile):
            self.notifier(_('You are late, you will be logged out in LESS than 2 minutes'))

        if ispasttime(self.limits, time):
            self.notifier(_('Your time is up, you will be logged out in LESS than 2 minutes'))
	return True

    '''
    Returns a formated string with the time left for a user
    '''
    def timeleftstring(self, h, m, s):
        #TODO: Need to find a better way to have plural form (or just use hours(s) )
        message = _('You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left') % {'hour': h, 'min': m, 'sec': s}

        #if h > 1 or h == 0:
            #if m > 1 or m == 0:
                #message = _('You have %(hour)s hours, %(min)s minutes and %(sec)s seconds left') % {'hour': h, 'min': m, 'sec': s)
            #else:
                #message = _('You have %(hour)s hours, %(min)s minute and %(sec)s seconds left') % {'hour': h, 'min': m, 'sec': s)
        #else:
            #if m > 1 or m == 0:
                #message = _('You have %(hour)s hour, %(min)s minutes and %(sec)s seconds left') % {'hour': h, 'min': m, 'sec': s)
            #else:
                #message = _('You have %(hour)s hour, %(min)s minute and %(sec)s seconds left') % {'hour': h, 'min': m, 'sec': s)

        return message

    '''
    Periodic notifier, gives notifications to the user.
    Runs every 15 minutes, as long as time left > 15 minutes
    '''
    def pnotifier(self):

        if not self.gettime(self.timefile):
            return True

        index = int(strftime("%w"))

        # How much time if left?
        usedtime = self.gettime(self.timefile)
        timeleft = self.limits[index] - usedtime
        timeuntil = self.timeofbto(index) - self.now()
        tuntil = timeuntil.seconds

        # What is less?
        if timeleft <= tuntil:
            left = timeleft
        else:
            left = tuntil

        # If the time is up, notifications is taken care of by checkLimits
        if left <= 0:
            return True
        h, m, s = self.fractSec(left)
        message = self.timeleftstring(h, m, s)
        self.notifier(message)

        # if time left is less than 5 minutes, notify every second minute
        if left < 300:
            gobject.timeout_add(2 * 60 * 1000, self.pnotifier)
            return False

        # if time left is less than 15 minutes, notify every 5 minutes
        if left < 900:
            gobject.timeout_add(5 * 60 * 1000, self.pnotifier)
            return False

        return True

    '''
    Acctuall notifier
    '''
    def notifier(self, message):
        index = int(strftime("%w"))
        # Don't notify an unrestricted user
        if not isrestricteduser(self.username, self.limits[index]):
            return
        title = "Timekpr"
        # Gnome and XFCE can user notify-send
        if self.get_de() == 'GNOME' or self.get_de() == 'XFCE':
            getcmdoutput('notify-send --icon=gtk-dialog-warning --urgency=critical -t 3000 "' + title + '" "' + message + '"')
        else:
            # KDE4 uses dbus
            if self.kde_version() == 4:
                import sys
                import dbus
                kn = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
                # Should get rid of "kde" in second argument, but it did not work with "timekpr-client
                i = kn.event("warning", "kde", [], message, [0,0,0,0], [], 0, dbus_interface="org.kde.KNotify")
                sleep(10)
                kn.closeNotification(i)
            else:
                # KDE3 and friends use dcop
                getcmdoutput('dcop knotify default notify notifying timekpr-client "' + message + '" "" "" 16 0')

    def main(self):
        gtk.main()

#Start
if __name__ == "__main__":
    tc = TimekprClient()
    tc.main()
