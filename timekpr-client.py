#!/usr/bin/python

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

import gtk
import gobject
import os
import os.path
from time import strftime, sleep
import datetime
import timekpr.pam as pam
import timekpr.common as common
import timekpr.dirs as dirs

import locale
import gettext
import sys

class TimekprClient:
    def __init__(self):
        self.VAR = common.timekpr_variables
        self.checkInterval = 60
        self.tray = gtk.StatusIcon()
        self.red = os.path.join(dirs.SHARED_DIR, 'timekpr32x32.png')
        self.green = os.path.join(dirs.SHARED_DIR, 'padlock-green.png')
        self.tray.set_from_file(self.red)
        self.tray.set_tooltip('timekpr-client')
        self.tray.set_visible(True)
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.username = os.getenv('USER')
        self.timefile = os.path.join(dirs.WORK_DIR, self.username + '.time')
        self.allowfile = os.path.join(dirs.WORK_DIR, self.username + '.allow')
        self.conffile = os.path.join(dirs.SETTINGS_DIR, self.username)
        self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)
        self.timer = None
        self.checkLimits()
        #Add a gobject loop to check limits:
        self.timer = gobject.timeout_add(self.checkInterval * 1000, self.checkLimits)
        #Add a notifier every 15 minutes
        gobject.timeout_add(15 * 60 * 1000, self.pnotifier)
        self.click = False
        self.lastNotified = datetime.datetime.now()

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
        if "KDE_FULL_SESSION" in os.environ or "KDE_MULTIHEAD" in os.environ:
            return "KDE"
        elif "GNOME_DESKTOP_SESSION_ID" in os.environ or "GNOME_KEYRING_SOCKET" in os.environ:
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
        self.click = True
        self.pnotifier()

    '''
    Right click on tray icon
    Should we add a menu to this action?
    '''
    def on_popup_menu(self, status, button, time):
        self.click = True
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
        # Hour Plurality
        if h == 1:
            hplr = "hour"
        elif h > 1:
            hplr = "hours"

        # Minute Plurality
        if m ==1:
            mplr = "minute"
        elif  m > 1:
            mplr = "minutes"

        # Second Plurality
        if s == 1:
            splr = "second"
        elif s > 1:
            splr = "seconds"

        # Printing Correctly
        if h >= 1 and m >= 1 and s >= 1:
            message = _('You have %(hour)s %(hplr)s, %(min)s %(mplr)s and %(sec)s %(splr)s left') % {'hour': h, 'hplr': hplr, 'min': m, 'mplr': mplr, 'sec': s, 'splr': splr}
        elif h >= 1 and m >= 1 and s == 0:
            message = _('You have %(hour)s %(hplr)s, %(min)s %(mplr)s left') % {'hour': h, 'hplr': hplr, 'min': m, 'mplr': mplr,}
        elif h >= 1 and m == 0 and s >= 1:
            message = _('You have %(hour)s %(hplr)s and %(sec)s %(splr)s left') % {'hour': h, 'hplr': hplr, 'sec': s, 'splr': splr}
        elif h >= 1 and m == 0 and s == 0:
            message = _('You have %(hour)s %(hplr)s left') % {'hour': h, 'hplr': hplr,}

        if h == 0 and m >= 1 and s >= 1:
            message = _('You have %(min)s %(mplr)s and %(sec)s %(splr)s left') % {'min': m, 'mplr': mplr, 'sec': s, 'splr': splr}
        elif h == 0 and m >= 1 and s == 0:
            message = _('You have %(min)s %(mplr)s left') % {'min': m, 'mplr': mplr,}
        elif h == 0 and m == 0 and s >= 1:
            message = _('You have %(sec)s %(splr)s left') % {'sec': s, 'splr': splr}


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

        # if time left is less than 8 minutes, notify every second minute
        if left < 480 and not self.click:
            gobject.timeout_add(2 * 60 * 1000, self.pnotifier)
            return False

        # if time left is less than 20 minutes, notify every 5 minutes
        if left < 1200 and not self.click:
            gobject.timeout_add(5 * 60 * 1000, self.pnotifier)
            return False

        self.click = False
        return True

    '''
    Actual notifier
    '''
    def notifier(self, message):
        index = int(strftime("%w"))
        # Don't notify an unrestricted user
        if not isrestricteduser(self.username, self.limits[index]):
            return
        title = "timekpr"
        # Don't notify if we just gave a notification
        if (datetime.datetime.now() - self.lastNotified).seconds < 5:
            return
        # Gnome and XFCE can user notify-send
        if self.get_de() == 'GNOME' or self.get_de() == 'XFCE':
            getcmdoutput('notify-send --icon=gtk-dialog-warning --urgency=critical -t 3000 "' + title + '" "' + message + '"')
        elif self.get_de() == 'KDE':
            # KDE4 uses dbus
            if self.kde_version() == 4:
                import sys
                import dbus
                duration = 7
                nid = 0
                bus = dbus.SessionBus()
                notify = dbus.Interface(bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications'), 'org.freedesktop.Notifications')
                title="timekpr notification"
                #message = "<div><img style=\"float: left; position: bottom; margin: 0px 5px 40px 0px;\" src=\"<path to image here>\" /><p style=\"font-size: x-large;\">Message</p></div>"
                nid = notify.Notify('', nid, '', title, message, '', '', -1)
                sleep(duration)
                notify.CloseNotification(nid)
            else:
                # KDE3 and friends use dcop
                getcmdoutput('dcop knotify default notify notifying timekpr-client "' + message + '" "" "" 16 0')
        else:
            # Not using Gnome, XFCE or KDE, try standard notification with notify-send
            getcmdoutput('notify-send --icon=gtk-dialog-warning --urgency=critical -t 3000 "' + title + '" "' + message + '"')

        self.lastNotified = datetime.datetime.now()

    def main(self):
        gtk.main()

#Start
if __name__ == "__main__":
    tc = TimekprClient()
    tc.main()
