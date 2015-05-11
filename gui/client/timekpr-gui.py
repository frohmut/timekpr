#!/usr/bin/env python
""" The graphical user interface for timekpr configuration.
	Copyright / License: See COPYRIGHT.txt
"""

import re
from os import remove, mkdir, geteuid, getenv
from os.path import isdir, isfile, realpath, dirname
from time import strftime, sleep
from pwd import getpwnam
from spwd import getspall

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

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
ngettext = gettext.ngettext

#If DEVACTIVE is true, it uses files from local directory
DEVACTIVE = False

#IMPORT
if DEVACTIVE:
	from sys import path
	path.append('.')
from timekprpam import *
from timekprcommon import *

#timekpr.conf variables (dictionary variable)
VAR = getvariables(DEVACTIVE)
version = getversion()

#Check if admin/root
def checkifadmingui():
	if geteuid() != 0:
		dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, _("You need to have administrative privileges to run timekpr-gui"))
		dlg.set_default_response(gtk.RESPONSE_CLOSE)
		dlg.run()
		dlg.destroy()
		exit("Error: You need to have administrative privileges to run timekpr")

checkifadmingui()

#Create configuration folder if not existing
if not isdir(VAR['TIMEKPRDIR']):
	mkdir(VAR['TIMEKPRDIR'])
if not isdir(VAR['TIMEKPRWORK']):
	mkdir(VAR['TIMEKPRWORK'])
if not isdir(VAR['TIMEKPRSHARED']):
	exit('Error: Could not find the shared directory %s' % VAR['TIMEKPRSHARED'])

#Check if it is a regular user, with userid within UID_MIN and UID_MAX.
def isnormal(username):
	#FIXME: Hide active user - bug #286529
	if (getenv('SUDO_USER') and username == getenv('SUDO_USER')):
		return False

	try:
		pwnam = getpwnam(username)
	except KeyError:
			return False

	userid = int(pwnam[2])
	logindefs = open('/etc/login.defs')
	uidminmax = re.compile('^UID_(?:MIN|MAX)\s+(\d+)', re.M).findall(logindefs.read())

	if uidminmax[0] < uidminmax[1]:
		uidmin = int(uidminmax[0])
		uidmax = int(uidminmax[1])
	else:
		uidmin = int(uidminmax[1])
		uidmax = int(uidminmax[0])

	if uidmin <= userid <= uidmax:
		return True
	else:
		return False

def rm(f):
	try:
		remove(f)
	except OSError:
		pass

class timekprGUI:
	def __init__(self):
		dummy = _('Timekpr Control Panel')
		dummy = _('Timekpr Client')

		gladefile = VAR['TIMEKPRSHARED'] + '/timekpr.glade'
		self.wTree = gtk.glade.XML(gladefile, 'mainwindow', APP_NAME)

		self.get_limit_spin()
		self.get_from_spin()
		self.get_to_spin()
		self.get_labels()

		self.singleLimits = self.wTree.get_widget("singleLimits")
		self.singleBoundaries = self.wTree.get_widget("singleBoundaries")
		self.limitCheck = self.wTree.get_widget("limitCheck")
		self.boundariesCheck = self.wTree.get_widget("boundariesCheck")
		self.userSelect = self.wTree.get_widget("userSelect")
		self.rewardSpin = self.wTree.get_widget("rewardSpin")
		self.labelrewardspin = self.wTree.get_widget("labelrewardspin")
		self.labeluserstatus = self.wTree.get_widget("labeluserstatus")

		self.limiticon = self.wTree.get_widget("imagelimited1")
		self.boundariesicon = self.wTree.get_widget("imagelimited2")
		self.alldayloginicon = self.wTree.get_widget("imagealldaylogin")
		self.lockedicon = self.wTree.get_widget("imagelocked")
		self.timeleftlabel = self.wTree.get_widget("timeleftlabel")

		self.extendLimitsButton = self.wTree.get_widget("extendLimitsButton")
		self.rewardButton = self.wTree.get_widget("rewardButton")
		self.clearallButton = self.wTree.get_widget("ClearAllRestrictionsButton")
		self.resettimeButton = self.wTree.get_widget("ResetTimeButton")
		self.lockLabel = self.wTree.get_widget("labelunlockbutton")

		self.statusbar = self.wTree.get_widget("statusbar")
		self.statusbarCID = self.statusbar.get_context_id("timekprstatus")

		self.limits = []

		dic = {
			"on_limitCheck_toggled": self.limitCheck_toggled,
			"on_boundariesCheck_toggled": self.boundariesCheck_toggled,
			"on_rewardButton_clicked": self.rewardButton_clicked,
			"on_extendLimitsButton_clicked": self.extendLimitsButton_clicked,
			"on_ClearAllRestrictionsButton_clicked": self.clearallrestrictions,
			"on_ResetTimeButton_clicked": self.resettimefile,
			"on_UnlockButton_clicked": self.lockunlockaccount,
			"on_apply_clicked": self.apply_clicked,
			"on_singleBoundaries_toggled": self.singleBoundariesCheck_toggled,
			"on_singleLimits_toggled": self.singleLimitsCheck_toggled,
			"on_userSelect_toggled": self.read_settings,
			"on_refresh_clicked": self.refreshButton_clicked,
			"on_cancel_clicked": self.cancel_clicked,
			"on_aboutmenuitem_select": self.showaboutdialog,
			'gtk_main_quit': gtk.main_quit
		}
		self.wTree.signal_autoconnect(dic)

		#Using /etc/shadow spwd module
		for userinfo in getspall():
			if isnormal(userinfo[0]):
				self.userSelect.append_text(userinfo[0])
				self.userSelect.set_active(0)

		#Ensure we have at least one available normal user
		if self.userSelect.get_active_text() is None:
			dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, _("You need to have at least one normal user available to configure timekpr"))
			dlg.set_default_response(gtk.RESPONSE_CLOSE)
			dlg.run()
			dlg.destroy()
			exit("Error: You need to have at least one normal user available to configure timekpr")

		self.read_settings(self)
		return

	def statusrefresh(self, widget, msgid):
		self.statusbar.remove(self.statusbarCID, msgid)

	def statusmessage(self, widget, message):
		msgid = self.statusbar.push(self.statusbarCID, strftime("%Y-%m-%d %H:%M:%S ") + message)
		timeoutid = gobject.timeout_add(6000, self.statusrefresh, self, msgid)

	def showaboutdialog(self, widget):
		self.aboutdialog = gtk.glade.XML(VAR['TIMEKPRSHARED'] + '/timekpr.glade', 'aboutdialog')
		self.aboutd = self.aboutdialog.get_widget('aboutdialog')
		self.aboutd.set_version(version)
		self.aboutd.set_translator_credits(_("translator-credits"))
		self.aboutd.set_comments(_('Keep control of computer usage'))
		self.aboutd.show_all()
		self.aboutd.run()
		self.aboutd.destroy()

	def lockunlockaccount(self, widget):
		if self.lockLabel.get_label() == _('Lock account'):
			#lock account
			lockuser(self.user)
			statusmsg = _("Locked account %s") % (self.user)
			self.statusmessage(self, statusmsg)
			self.read_settings_nolimits(self)
		else:
			#unlock account
			unlockuser(self.user)
			#remove .lock file
			lockf = VAR['TIMEKPRDIR'] + '/' + self.user + '.lock'
			rm(lockf)
			logoutf = VAR['TIMEKPRWORK'] + '/' + self.user + '.logout'
			rm(logoutf)
			latef = VAR['TIMEKPRWORK'] + '/' + self.user + '.late'
			rm(latef)
			statusmsg = _("Unlocked account %s") % self.user
			self.statusmessage(self, statusmsg)
			self.read_settings_nolimits(self)

	def clearallrestrictions(self, widget):
		#clears all limits and their files
		#FIXME: A yes/no confirmation would be handy here
		timef = VAR['TIMEKPRWORK'] + '/' + self.user + '.time'
		logoutf = VAR['TIMEKPRWORK'] + '/' + self.user + '.logout'
		latef = VAR['TIMEKPRWORK'] + '/' + self.user + '.late'
		allowf = VAR['TIMEKPRWORK'] + '/' + self.user + '.allow'
		#Should remove .allow file? It's not a restriction
		rm(timef)
		rm(logoutf)
		rm(latef)
		rm(allowf)
		#Remove boundaries
		removeuserlimits(self.user)
		#Remove limits
		configf = VAR['TIMEKPRDIR'] + '/' + self.user
		rm(configf)
		#Unlock user
		unlockuser(self.user)

		statusmsg = _("Removed all restrictions for account %s") % self.user
		self.statusmessage(self, statusmsg)
		self.read_settings(self)

	def resettimefile(self, widget):
		#clear the .time file
		timefile = VAR['TIMEKPRWORK'] + '/' + self.user + '.time'
		rm(timefile)
		statusmsg = _("Cleared used up time for account %s") % self.user
		self.statusmessage(self, statusmsg)
		self.read_settings_nolimits(self)

	def rewardButton_clicked(self, widget):
		arg = self.rewardSpin.get_value_as_int()
		timefile = VAR['TIMEKPRWORK'] + '/' + self.user + '.time'
		if isfile(timefile):
			f = open(timefile)
			tlast = int(f.read())
			f.close()
		else:
			tlast = 0
		tnew = tlast - arg * 60
		f = open(timefile, 'w')
		f.write(str(tnew))
		f.close()
		statusmsg = _("Applied reward of %(num)s minute(s) to account %(user)s") % {'num': arg, 'user': self.user}
		self.statusmessage(self, statusmsg)
		self.read_settings_nolimits(self)

	def extendLimitsButton_clicked(self, widget):
		#UPDATE: extend limits button is now "Bypass for today"
		#It now is the same as changing boundaries from 0 to 24 for today's day of the week.
		#.allow can still be useful - active (logged in user accounts) won't be killed
		index = int(strftime("%w"))
		wfrom = self.fromtolimits[0]
		wto = self.fromtolimits[1]
		wfrom[index] = '0'
		wto[index] = '24'
		removeuserlimits(self.user)
		adduserlimits(self.user, wfrom, wto)
		allowfile = VAR['TIMEKPRWORK'] + '/' + self.user + '.allow'
		f = open(allowfile, 'w').close()
		statusmsg = _("Set access hours to 00-24 on %(day)s for account %(user)s") % {'day': strftime("%A"), 'user': self.user}
		self.statusmessage(self, statusmsg)
		self.read_settings(self)

	def refreshButton_clicked(self, widget):
		statusmsg = _("Refreshed setting values from account %s") % self.user
		self.statusmessage(self, statusmsg)
		self.read_settings(self)

	def cancel_clicked(self, widget):
		gtk.main_quit()

	def get_limit_spin(self):
		self.limitSpin = list()
		self.limitSpin.append(self.wTree.get_widget("limitSpin0"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin1"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin2"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin3"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin4"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin5"))
		self.limitSpin.append(self.wTree.get_widget("limitSpin6"))

	def get_from_spin(self):
		self.fromSpin = list()
		self.fromSpin.append(self.wTree.get_widget("fromSpin0"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin1"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin2"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin3"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin4"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin5"))
		self.fromSpin.append(self.wTree.get_widget("fromSpin6"))

	def get_to_spin(self):
		self.toSpin = list()
		self.toSpin.append(self.wTree.get_widget("toSpin0"))
		self.toSpin.append(self.wTree.get_widget("toSpin1"))
		self.toSpin.append(self.wTree.get_widget("toSpin2"))
		self.toSpin.append(self.wTree.get_widget("toSpin3"))
		self.toSpin.append(self.wTree.get_widget("toSpin4"))
		self.toSpin.append(self.wTree.get_widget("toSpin5"))
		self.toSpin.append(self.wTree.get_widget("toSpin6"))

	def get_labels(self):
		self.lb = list()
		self.lb.append(self.wTree.get_widget("lb0"))
		self.lb.append(self.wTree.get_widget("lb1"))
		self.lb.append(self.wTree.get_widget("lb2"))
		self.lb.append(self.wTree.get_widget("lb3"))
		self.lb.append(self.wTree.get_widget("lb4"))
		self.lb.append(self.wTree.get_widget("lb5"))
		self.lb.append(self.wTree.get_widget("lb6"))
		self.ll = list()
		self.ll.append(self.wTree.get_widget("ll0"))
		self.ll.append(self.wTree.get_widget("ll1"))
		self.ll.append(self.wTree.get_widget("ll2"))
		self.ll.append(self.wTree.get_widget("ll3"))
		self.ll.append(self.wTree.get_widget("ll4"))
		self.ll.append(self.wTree.get_widget("ll5"))
		self.ll.append(self.wTree.get_widget("ll6"))

	def readfromtolimit(self, widget):
		#from-to time limitation (aka boundaries) - time.conf
		if isuserlimited(self.user):
			#Get user time limits (boundaries) as lists from-to
			bfrom = self.fromtolimits[0]
			bto = self.fromtolimits[1]

			for i in range(7):
				self.fromSpin[i].set_value(float(bfrom[i]))
				self.toSpin[i].set_value(float(bto[i]))
			# Use boundaries?
			ub = True
			# Single boundaries? (set per day)
			sb = False
			#Are all boundaries the same?
			#If they're not same, activate single (per day) boundaries
			if [bfrom[0]] * 7 != bfrom or [bto[0]] * 7 != bto:
				sb = True
			#Even if boundaries are Al0000-2400, return False
			if not sb and bfrom[0] == '0' and bto[0] == '24':
				ub = False
			self.boundariesCheck.set_active(ub)
			self.singleBoundaries.set_active(sb)
		else:
			for i in range(7):
				self.fromSpin[i].set_value(7)
				self.toSpin[i].set_value(22)
			self.boundariesCheck.set_active(False)
			self.singleBoundaries.set_active(False)

	def readdurationlimit(self, widget):
		#time length limitation
		configFile = VAR['TIMEKPRDIR'] + '/' + self.user
		del self.limits[:]
		if isfile(configFile):
			fileHandle = open(configFile)
			self.limits = fileHandle.readline()
			self.limits = self.limits.replace("limit=( ", "")
			self.limits = self.limits.replace(")", "")
			self.limits = self.limits.split(" ")

			for i in range(7):
				self.limitSpin[i].set_value(float(self.limits[i]) / 60)

			# Single limits? (set per day)
			sl = False
			# Use limits?
			ul = True

			for i in range(1, 7):
				if self.limits[i] != self.limits[i-1]:
					sl = True

			if self.limits[0] == '86400' and not sl:
				ul = False
			self.limitCheck.set_active(ul)
			self.singleLimits.set_active(sl)
		else:
			for i in range(7):
				self.limitSpin[i].set_value(300)
			self.limitCheck.set_active(False)
			self.singleLimits.set_active(False)

	def statusicons(self, widget, uislocked):
		#Set icons in status gtk-yes or gtk-no
		lockgreen = VAR['TIMEKPRSHARED'] + '/padlock-green.png'
		lockred = VAR['TIMEKPRSHARED'] + '/padlock-red.png'
		iconyes = gtk.STOCK_YES
		iconno = gtk.STOCK_NO
		iconsize = gtk.ICON_SIZE_BUTTON
		#limitSpin status is already set, so we can use it
		#self.spinlimitvalue = self.wTree.get_widget("limitSpin" + strftime('%w')).get_value()
		if not isuserlimitedtoday(self.user) and not uislocked:
			self.alldayloginicon.set_from_stock(iconyes, iconsize)
		else:
			self.alldayloginicon.set_from_stock(iconno, iconsize)

		if self.limitCheck.get_active():
			self.limiticon.set_from_file(lockred)
		else:
			self.limiticon.set_from_file(lockgreen)

		if self.boundariesCheck.get_active():
			self.boundariesicon.set_from_file(lockred)
		else:
			self.boundariesicon.set_from_file(lockgreen)

		if uislocked:
			self.lockedicon.set_from_file(lockred)
		else:
			self.lockedicon.set_from_file(lockgreen)

		index = int(strftime("%w"))
		try:
			limit = int(self.limits[index])
		except IndexError:
			limit = 86400

		timefile = VAR['TIMEKPRWORK'] + '/' + self.user + '.time'
		used = 0
		if isfile(timefile) and fromtoday(timefile):
			t = open(timefile)
			used = int(t.readline())
			t.close()
		left = limit - used
		m, s = divmod(left, 60)
		self.timeleftlabel.set_label(ngettext('%(min)s minute', '%(min)s minutes', abs(m)) % {'min': m})

	def buttonstates(self,widget, uislocked):
		if uislocked:
			self.lockLabel.set_label(_('Unlock account'))
		else:
			self.lockLabel.set_label(_('Lock account'))

		if self.limitCheck.get_active():
			timefile = VAR['TIMEKPRWORK'] + '/' + self.user + '.time'
			if isfile(timefile):
				self.resettimeButton.set_sensitive(True)
			else:
				self.resettimeButton.set_sensitive(False)
			#Reward button should add time even if .time is not there?
			self.rewardButton.set_sensitive(True)
			self.rewardSpin.set_sensitive(True)
			self.labelrewardspin.set_sensitive(True)
		else:
			self.resettimeButton.set_sensitive(False)
			self.rewardButton.set_sensitive(False)
			self.rewardSpin.set_sensitive(False)
			self.labelrewardspin.set_sensitive(False)

		if self.boundariesCheck.get_active():
			index = int(strftime("%w"))
			wfrom = self.fromtolimits[0]
			wto = self.fromtolimits[1]
			if wfrom[index] != '0' or wto[index] != '24':
				self.extendLimitsButton.set_sensitive(True)
			else:
				self.extendLimitsButton.set_sensitive(False)
		else:
			self.extendLimitsButton.set_sensitive(False)

	def read_settings(self, widget):
		self.user = self.userSelect.get_active_text()
		uislocked = isuserlocked(self.user)
		self.fromtolimits = getuserlimits(self.user)
		self.readfromtolimit(self)
		self.readdurationlimit(self)
		self.labeluserstatus.set_label(_('Status for') + ' <span weight="bold">' + self.user + '</span>')
		self.statusicons(self, uislocked)
		self.buttonstates(self, uislocked)

	def read_settings_nolimits(self, widget):
		uislocked = isuserlocked(self.user)
		self.statusicons(self, uislocked)
		self.buttonstates(self, uislocked)

	def boundariesCheck_toggled(self, widget):
		if self.boundariesCheck.get_active():
			self.fromSpin[0].set_sensitive(True)
			self.toSpin[0].set_sensitive(True)
			self.singleBoundaries.set_sensitive(True)
			self.wTree.get_widget("labelTo").set_sensitive(True)
			self.wTree.get_widget("labelFrom").set_sensitive(True)
			self.lb[0].set_sensitive(True)
		else:
			self.fromSpin[0].set_sensitive(False)
			self.toSpin[0].set_sensitive(False)
			self.singleBoundaries.set_sensitive(False)
			self.wTree.get_widget("labelTo").set_sensitive(False)
			self.wTree.get_widget("labelFrom").set_sensitive(False)
			self.lb[0].set_sensitive(False)
		self.singleBoundariesCheck_toggled(self)

	def singleBoundariesCheck_toggled(self, widget):
		if self.singleBoundaries.get_active() and self.boundariesCheck.get_active():
			for i in range(1, 7):
				self.fromSpin[i].set_sensitive(True)
				self.toSpin[i].set_sensitive(True)
				self.lb[i].set_sensitive(True)
			self.lb[0].set_text(_("	Sun	 "))
		else:
			for i in range(1, 7):
				self.fromSpin[i].set_sensitive(False)
				self.toSpin[i].set_sensitive(False)
				self.lb[i].set_sensitive(False)
			self.lb[0].set_text(_("Every day"))

	def limitCheck_toggled(self, widget):
		if self.limitCheck.get_active():
			self.limitSpin[0].set_sensitive(True)
			self.singleLimits.set_sensitive(True)
			self.wTree.get_widget("labelMinutes").set_sensitive(True)
			self.ll[0].set_sensitive(True)
		else:
			self.limitSpin[0].set_sensitive(False)
			self.singleLimits.set_sensitive(False)
			self.wTree.get_widget("labelMinutes").set_sensitive(False)
			self.ll[0].set_sensitive(False)
		self.singleLimitsCheck_toggled(self)

	def singleLimitsCheck_toggled(self, widget):
		if self.singleLimits.get_active() and self.limitCheck.get_active():
			for i in range(1, 7):
				self.ll[i].set_sensitive(True)
				self.limitSpin[i].set_sensitive(True)
			self.ll[0].set_text(" " + _("Sun") + " ")
		else:
			for i in range(1, 7):
				self.ll[i].set_sensitive(False)
				self.limitSpin[i].set_sensitive(False)
			self.ll[0].set_text(_("Every day"))

	def apply_clicked(self, widget):
		space = " "
		limit = "limit=( 86400 86400 86400 86400 86400 86400 86400 )"
		#timekprpam.py adduserlimits() uses lists with numbers as strings
		bFrom = ['0'] * 7
		bTo = ['24'] * 7

		if self.limitCheck.get_active():
			if self.singleLimits.get_active():
				limit = "limit=("
				for i in range(7):
					limit = limit + space + str(self.limitSpin[i].get_value_as_int() * 60)
				limit = limit + space + ")"
			else:
				limit = "limit=("
				for i in range(7):
					limit = limit + space + str(self.limitSpin[0].get_value_as_int() * 60)
				limit = limit + space + ")"
		if self.boundariesCheck.get_active():
			if self.singleBoundaries.get_active():
				bFrom = []
				bTo = []
				for i in range(7):
					bFrom.append(str(self.fromSpin[i].get_value_as_int()))
					bTo.append(str(self.toSpin[i].get_value_as_int()))
			else:
				bFrom = []
				bTo = []
				for i in range(7):
					bFrom.append(str(self.fromSpin[0].get_value_as_int()))
					bTo.append(str(self.toSpin[0].get_value_as_int()))
		configFile = VAR['TIMEKPRDIR'] + '/' + self.user
		if self.limitCheck.get_active():
			fH = open(configFile, 'w')
			fH.write(limit + "\n")
			fH.close()
		else:
			rm(configFile)

		#No need to check if boundaries are active or not, apply the default or custom limits
		#Remove old user limits (boundaries)
		rb = removeuserlimits(self.user)
		#Add new limits (boundaries)
		ab = adduserlimits(self.user, bFrom, bTo)

		statusmsg = _("Applied limit changes for account %s") % self.user
		self.statusmessage(self, statusmsg)
		self.read_settings(self)

if __name__ == "__main__":
	timekprGUI()
	gtk.main()
