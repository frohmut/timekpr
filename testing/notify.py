#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import os, os.path
import pynotify


if __name__ == '__main__':
	if not pynotify.init("Timekpr notification"):
		exit(1)

#	n = pynotify.Notification("Moo title", "test")
	n = pynotify.Notification('Moo title', 'test', 'file://' + os.getcwd() + '/logo/stop-hand-clock-small.png')
	n.set_urgency(pynotify.URGENCY_CRITICAL)
	n.set_timeout(10000) # 10 seconds
	n.set_category('device')

	#Call an icon
#	helper = gtk.Button()
#	icon = helper.render_icon(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
#	n.set_icon_from_pixbuf(icon)

	if not n.show():
		print('Failed to send notification')
		exit(1)
