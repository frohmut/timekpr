#!/bin/bash
if [ ! -d /usr/local/bin ]; then
	mkdir /usr/local/bin
fi
if [ ! -d /usr/share/timekpr ]; then
	mkdir /usr/share/timekpr
fi
wget nedberg.net/timekpr/timekpr-addtime -O /usr/local/bin/timekpr-addtime
wget nedberg.net/timekpr/timekpr-extend -O /usr/local/bin/timekpr-extend
wget nedberg.net/timekpr/timekpr -O /usr/local/bin/timekpr
wget nedberg.net/timekpr/timekpr-gui -O /usr/local/bin/timekpr-gui
wget nedberg.net/timekpr/timekpr.glade -O /usr/share/timekpr/timekpr.glade
chmod 744 /usr/local/bin/timekpr-addtime /usr/local/bin/timekpr-extend /usr/local/bin/timekpr /usr/local/bin/timekpr-gui
if [ ! -d /var/lib/timekpr ]; then
	mkdir /var/lib/timekpr
fi
