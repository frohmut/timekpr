#!/bin/bash
if [ ! -d /usr local/bin ]; then
	mkdir /usr/local/bin
fi
apt-get install libnotify-bin
wget nedberg.net/timekpr/addtime.sh -O /usr/local/bin/addtime.sh
wget nedberg.net/timekpr/extendlimits.sh -O /usr/local/bin/extendlimits.sh
wget nedberg.net/timekpr/timekpr.sh -O /usr/local/bin/timekpr.sh
wget nedberg.net/timekpr/timekprGUI.py -O /usr/local/bin/timekprGUI.py
wget nedberg.net/timekpr/Timekpr.glade -O /usr/local/bin/Timekpr.glade
chmod 744 /usr/local/bin/addtime.sh /usr/local/bin/extendlimits.sh /usr/local/bin/timekpr.sh /usr/local/bin/timekprGUI.py /usr/local/bin/Timekpr.glade
if [ ! -d /var/lib/timekpr ]; then
	mkdir /var/lib/timekpr
fi