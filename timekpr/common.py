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

# import common
import gtk
from os.path import isfile, getmtime
from os import geteuid
from time import strftime, localtime
import pynotify

# import timekpr-related
from pam import *
import dirs

# Import i18n
import locale
import gettext

timekpr_version = '0.3.0'

# Translation stuff
local_path = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')
domain = 'timekpr'
gettext.bindtextdomain(domain, local_path)
gettext.textdomain(domain)
_ = gettext.gettext
# FIXME: For translations in other files, use: _ = common._

""" Variables
    * GRACEPERIOD:
    This is the grace period, where a notification pops up letting the users
    know that their time usage will be over soon.
    Users are given by default 120 seconds to finish up their work.
    Limit is expressed in seconds, e.g. 120 means 2 minutes
    * POLLTIME: How often should the script check the timelogs.
    Setting is expressed in seconds, e.g. 45 means 45 seconds.
    * DEBUGME: True keeps a logfile, False does not.
    * LOCKLASTS: Default lock period
    Setting can be day(s), hour(s), minute(s), month(s) (30 days)
    Example: 5 hours
"""

# FIXME: dirs in these variables are just for transition
#        Use dirs.SOMETHING_HERE instead of VAR['']
timekpr_variables = {
    'GRACEPERIOD'  : 120,
    'POLLTIME'     : 45,
    'DEBUGME'      : True,
    'LOCKLASTS'    : '1 hour',
    'LOGFILE'      : dirs.LOG_FILE,
    'TIMEKPRDIR'   : dirs.TIMEKPR_SETTINGS_DIR,
    'TIMEKPRSHARED': dirs.TIMEKPR_SHARED_DIR,
    'TIMEKPRDAEMON': dirs.TIMEKPR_DAEMON_DIR,
    'TIMEKPRWORK'  : dirs.TIMEKPR_WORK_DIR,
}

# Check if admin/root
def checkifadmin():
    if geteuid() != 0:
        exit(_('Error: You need to have administrative privileges to run timekpr'))

def checkifadmingui():
    if geteuid() != 0:
        msg = _("You need to have administrative privileges to run timekpr-gui")
        errormsg(msg)

def errormsg(msg):
    """ Print an error message in GUI (GTK) and console (and exit) """
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
    dlg.set_default_response(gtk.RESPONSE_CLOSE)
    dlg.run()
    dlg.destroy()
    exit(msg)

def popup(title, msg):
    if not pynotify.init("timekpr warning"):
        exit("ERROR: timekpr -- Something wrong with pynotify")

    n = pynotify.Notification(title, msg, 'dialog-warning')
    n.set_urgency(pynotify.URGENCY_CRITICAL)

    if not n.show():
        exit('ERROR: timekpr -- Failed to send notification')

def getvariables():
    return timekpr_variables

def getcmdoutput(cmd):
    # TODO: timekpr-gui.py: Use it for "/etc/init.d/timekpr status" and a button enable/disable
    from os import popen
    # Execute a command, returns its output
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
    # Returns limits and from/to allowed hours
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

