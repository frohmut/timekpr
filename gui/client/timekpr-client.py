#!/usr/bin/python

try:
	from gi.repository import AppIndicator3 as AppIndicator
except ImportError:
	None

from gi.repository import Gtk, GLib
import os
from timekprpam import *
from timekprcommon import *
import locale
import gettext
import sys
import time
import datetime

from timekprcommon import getversion

# translation stuff
# get the local directory
# -----------------------
APP_NAME = "timekpr"
local_path = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, local_path)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
ngettext = gettext.ngettext
# -----------------------

class IndicatorTimekpr:
	def __init__(self):
		# get which DE we are running
		if os.getenv('XDG_CURRENT_DESKTOP') == "Unity":
			self.isAppIndicator = True
		else:
			self.isAppIndicator = False

		# define empty menu
		self.menu = Gtk.Menu()
		self.item_left = Gtk.MenuItem(_("Time left..."))
		self.menu.append(self.item_left)
		self.menu.append(Gtk.SeparatorMenuItem())
		self.item_cp = Gtk.MenuItem(_('Timekpr Control Panel'))
		self.menu.append(self.item_cp)
		self.menu.show_all()
		self.item_left.connect("activate", self.onClick)
		self.item_cp.connect("activate", self.onCP)

		# this is for Unity stuff
		if self.isAppIndicator:
			# init indicator itself (icon will be set later)
			self.ind = AppIndicator.Indicator.new("indicator-timekpr", "", AppIndicator.IndicatorCategory.APPLICATION_STATUS)
			self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)

			self.ind.set_menu(self.menu)
		# this is for Non-Unity stuff
		else:
			# set up tray
			self.tray = Gtk.StatusIcon()
			self.tray.set_visible(True)
			self.tray.connect('activate', self.onClick)
			self.tray.connect('popup-menu', self.onPopupMenu)

		# initialize timekpr related stuff
		self.initTimekpr()

	def onClick(self, evt):
		self.click = True
		self.regularNotifier()

	def onCP(self, evt):
		import subprocess
		rc = subprocess.call(['pkexec', 'timekpr-gui'])

	def onPopupMenu(self, status, button, time):
		# menu positioning
		def position(menu, status):
			return Gtk.StatusIcon.position_menu(self.menu, status)

		self.menu.popup(None, None, position, status, button, time)

	def initTimekpr(self):
		# get variables and set interval
		self.VAR = getvariables(False)
		self.checkInterval = 30
		self.timerLevelInEffect = 1

		self.notifyIntervalLevel1 = 10*60
		self.notifyIntervalLevel2 = 5*60
		self.notifyIntervalLevel3 = 2*60
		self.notifyIntervalLevel4 = 1*60

		# get both locked and unlocked icons
		self.limited_green = self.VAR['TIMEKPRSHARED'] + '/padlock-limited-green.png'
		self.limited_yellow = self.VAR['TIMEKPRSHARED'] + '/padlock-limited-yellow.png'
		self.limited_red = self.VAR['TIMEKPRSHARED'] + '/padlock-limited-red.png'
		self.unlimited_green = self.VAR['TIMEKPRSHARED'] + '/padlock-unlimited-green.png'

		# get username
		self.username = os.getenv('USER')

		# set up control files
		self.timefile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.time'
		self.allowfile = self.VAR['TIMEKPRWORK'] + '/' + self.username + '.allow'
		self.conffile = self.VAR['TIMEKPRDIR'] + '/' + self.username

		# nobody wanted info by clicking on the icon and other default stuff
		self.click = False
		self.firstNotif = True
		self.notifTimer = None
		self.timeSpentPrev = self.getTime(self.timefile)
		self.notificationLimits = (
			[0*60,1*60,'critical',self.limited_red,0]
			,[3*60,1*60,'critical',self.limited_red,1] # less than 3 mins - notification goes off every minute, urgency is critical, icon is red
			,[10*60,2*60,'normal',self.limited_yellow,2]
			,[25*60,5*60,'low',self.limited_green,3]
			,[9999999,10*60,'low',self.limited_green,4]
		)

		# initial check of the limits
		self.reReadConfigAndcheckLimits()

		# add a GLib loop to check limits:
		GLib.timeout_add_seconds(self.checkInterval, self.reReadConfigAndcheckLimits)

		# add a notifier for the first time to half minuten
		self.notifTimer = GLib.timeout_add_seconds(self.timerLevelInEffect, self.regularNotifier)

	def reReadConfigAndcheckLimits(self):
		# defaults
		urgency = 'low'

		# re-read settings in case they changed
		self.limits, self.bfrom, self.bto = readusersettings(self.username, self.conffile)

		# get the day
		index = int(strftime("%w"))

		# if the user is not a restricted user for this day, set the tray icon to green padlock
		if not isrestricteduser(self.username, self.limits[index]):
			# user is not limited
			if self.isAppIndicator:
				self.ind.set_icon(self.unlimited_green)
			else:
				self.tray.set_from_file(self.unlimited_green)

			# come back later
			return True
		elif self.firstNotif:
			# user is limited
			if self.isAppIndicator:
				self.ind.set_icon(self.limited_red)
			else:
				self.tray.set_from_file(self.limited_red)

		# get the time already spent
		time = self.getTime(self.timefile)

		# check if we have file, if not - exit
		if time == -0.1:
			return True

		# check if time changed too rapildly, we have to resched the notifier
		if abs(time - self.timeSpentPrev) > 2*self.checkInterval-1:
			# end the current callback
			GLib.source_remove(self.notifTimer)

			# add call very shortly
			self.timerLevelInEffect = 1
			self.notifTimer = GLib.timeout_add_seconds(self.timerLevelInEffect, self.regularNotifier)

		# store previous reading
		self.timeSpentPrev = time

		# get the time left
		left = self.getTimeLeft()

		# normalize time for display
		if left <= 0:
			left = 0
			urgency = 'critical'
		# in case more time added while very low on minutes
		elif self.timerLevelInEffect == 0 and left > 0:
			self.regularNotifier()

		# split hours, minutes, seconds
		h, m, s = self.fractSec(left)

		# indicators only
		if self.isAppIndicator:
			self.ind.set_label("("+str(h).rjust(2, "0")+":"+str(m).rjust(2, "0")+")", "")
		else:
			self.tray.set_tooltip_text("("+str(h).rjust(2, "0")+":"+str(m).rjust(2, "0")+")")

		# now if it arrives too early
		if isearly(self.bfrom, self.allowfile):
			self.notifyUser(_('You are early, you will be logged out in LESS than 2 minutes'), urgency)

		# now if it arrives too late
		if islate(self.bto, self.allowfile):
			self.notifyUser(_('You are late, you will be logged out in LESS than 2 minutes'), urgency)

		# now if allowed time is almost spent
		if ispasttime(self.limits, time):
			self.notifyUser(_('Your time is up, you will be logged out in LESS than 2 minutes'), urgency)

		# done
		return True

	# periodic notifier, gives notifications to the user
	def regularNotifier(self):
		# default values
		result = True
		timerLevelInEffectTmp = self.timerLevelInEffect
		urgency = 'low'

		# get the day
		index = int(strftime("%w"))

		# if there is time to check
		if self.getTime(self.timefile) == -0.1:
			return result
		# if the user is not a restricted user for this day
		elif not isrestricteduser(self.username, self.limits[index]):
			if self.firstNotif or self.click:
				self.notifyUser(_('Your time is not limited today'), 'low')
				self.click = False

				# restricted user - no more notifs
				self.timerLevelInEffect = 0
			result = False

		# first notification is no more
		self.firstNotif = False

		# we don't need to process any further
		if result != False:
			# get how much time is left
			left = self.getTimeLeft()

			# if the time is up, notifications is taken care of by reReadConfigAndcheckLimits
			if left < 0:
				# handled in read congig
				self.timerLevelInEffect = 0
				result = False

			# we don't need to process any further
			if result != False:
				# split hours, minutes, seconds
				h, m, s = self.fractSec(left)

				# build up message in human language :)
				message = self.calculateTimeLeftString(h, m, s)

				# check limits and do actions based on results
				for rLimit in self.notificationLimits:
					# if time left is more than 25 minutes, notify every 10 minutes
					if left < rLimit[0] + self.checkInterval + 5: 
						# set urgency
						urgency = rLimit[2]

						# if not clicked
						if not self.click:
							# new timer
							self.timerLevelInEffect = rLimit[1]

							# if limit has changed
							if timerLevelInEffectTmp != self.timerLevelInEffect:
								# depending on DE
								if self.isAppIndicator:
									self.ind.set_icon(rLimit[3])
								else:
									self.tray.set_from_file(rLimit[3])

								# change tmp for adjustments
								timerLevelInEffectTmp = self.timerLevelInEffect

								# calculate new interval: say if we have 26 mins notification will be scheduled at 16 mins, but the rule
								# is that if we have less than 25 mins, notification goes off every 5 mins, so that has to be at 25, 20, ... mins
								# to compensate that we need to schedule time to go off at 25 not 16
								if left - self.notificationLimits[rLimit[4]-1][0] < self.timerLevelInEffect:
									timerLevelInEffectTmp = left - self.notificationLimits[rLimit[4]-1][0]

								# set up new interval
								self.notifTimer = GLib.timeout_add_seconds(timerLevelInEffectTmp, self.regularNotifier)

								# end existing interval
								result = False

						# that's it
						break

				# notify (taking into account calculated urgency as well)
				self.notifyUser(message, urgency)

		# noone clicked us
		self.click = False

		# result
		return result

	# returns a formated string with the time left for a user
	def calculateTimeLeftString(self, h, m, s):
		# variables
		strLevel = 0

		## printing correctly
		# header
		# TRANSLATORS: this is a part of message "You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left" please translate accordingly
		message = _('You have') 

		# for hours
		if h > 0:
			# TRANSLATORS: this is a part of message "You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left" please translate accordingly
			messageTmp = ' ' + ngettext('%(hour)s hour', '%(hour)s hours', h) % {'hour': h}
			strLevel=strLevel+1
		else:
			messageTmp = ''

		# compose
		message = message + messageTmp

		# for minutes
		if m > 0:
			if strLevel > 0:
				messageTmp = ','
			else:
				messageTmp = ''

			# TRANSLATORS: this is a part of message "You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left" please translate accordingly
			messageTmp = messageTmp + ' ' + ngettext('%(min)s minute', '%(min)s minutes', m) % {'min': m}
			strLevel = strLevel + 1
		else:
			messageTmp = ''

		# compose
		message = message + messageTmp

		# for seconds
		if s > 0 or (m == 0 and h == 0):
			if strLevel > 0:
				messageTmp = ','
			else:
				messageTmp = ''

			# TRANSLATORS: this is a part of message "You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left" please translate accordingly
			messageTmp = messageTmp + ' ' + ngettext('%(sec)s second', '%(sec)s seconds', s) % {'sec': s}
			strLevel = strLevel + 1
		else:
			messageTmp = ''

		# compose
		# TRANSLATORS: this is a part of message "You have %(hour)s hour(s), %(min)s minute(s) and %(sec)s second(s) left" please translate accordingly
		message = message + messageTmp + ' ' + _('left')

		# final message
		return message

	def notifyUser(self, message, urgency):
		# defaults
		icon = 'gtk-dialog-info'
		durationSecs = 3
		durationMsecs = str(durationSecs * 1000)
		title = _('Timekpr notification')

		# based on urgency, choose different icon
		if urgency == 'normal':
			icon = 'gtk-dialog-warning'
		elif urgency == 'critical':
			icon = 'gtk-dialog-error'

		# KDE uses different tech to notify users
		if self.getSessionName() == 'KDE':
			# KDE4 uses dbus
			if self.getSessionVersion(self.getSessionName()) == 4:
				# do DBUS stuff
				import dbus

				# set up
				notificationId = 0
				sessionDbus = dbus.SessionBus()
				notifyInterface = dbus.Interface(bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications'), 'org.freedesktop.Notifications')
				
				# notify
				notificationId = notifyInterface.Notify('', notificationId, '', title, message, '', '', -1)
				sleep(duration) # we need to sleep explicitly
				notifyInterface.CloseNotification(notificationId)
			else:
				# KDE3 and friends use dcop
				getcmdoutput('dcop knotify default notify notifying timekpr-client "' + message + '" "" "" 16 0')
		else:
			# for the rest try standard notification
			getcmdoutput('notify-send --icon=' + icon + ' --urgency=critical' + ' -t ' + durationMsecs + ' "' + title + '" "' + message + '"')

	# returns the number of seconds a user has spent, False if user.time does not exist
	def getTime(self, tfile):
		# check for file
		if not isfile(tfile):
			return -0.1

		# get seconds spent
		t = open(tfile)
		time = int(t.readline())
		t.close()

		# pass back time
		return time

	def getTimeLeft(self):
		# get day
		index = int(strftime("%w"))

		# calculates how much time if left
		usedtime = self.getTime(self.timefile)
		timeleft = self.limits[index] - usedtime
		timeuntil = self.timeofbto(index) - datetime.datetime.now()
		tuntil = timeuntil.seconds

		# what is less (is "until" time earlier than limit)
		if timeleft <= tuntil:
			left = timeleft
		else:
			left = tuntil

		# return what's left :)
		return left

	# return the time limit
	def timeofbto(self, index):
		# current date
		y = datetime.date.today().year
		m = datetime.date.today().month
		d = datetime.date.today().day

		# to hour
		h = self.bto[index]

		# compose new date
		date = datetime.date(y, m, d)

		# correct date
		if h == 24:
			h = 0
			date = date + datetime.timedelta(days=1)

		# final calculation for date
		dt = datetime.datetime(date.year, date.month, date.day, h, 0, 0)

		# done
		return dt

	# divides time into larger pieces :)
	def fractSec(self, s):
		m, s = divmod(s, 60)
		h, m = divmod(m, 60)
		return h, m, s

	# this gets session information
	def getSessionName(self):
		return os.getenv('XDG_CURRENT_DESKTOP')
	
	# get KDE version
	def getSessionVersion(self, sessionName):
		# defaults
		version = 0

		# for KDE check KDE version
		if sessionName == "KDE":
			# get KDE version
			versionTmp = os.getenv('KDE_SESSION_VERSION')

			# get version
			if version == "\n" or version == "":
				version = 3
			else:
				version = int(versionTmp)

		# final version
		return version

	def quit(self):
		Gtk.main_quit()

def main():
	Gtk.main()

if __name__ == "__main__":
	indicator = IndicatorTimekpr()
	main()
