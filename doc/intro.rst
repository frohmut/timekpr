.. This document is written in rst.
.. Reference: http://docutils.sf.net/docs/user/rst/quickref.html
.. _intro:

=========
 timekpr
=========

Keep control of computer usage
==============================

INTRODUCTION
############

EXECUTABLES
-----------

1. timekpr
   The daemon service
	
2. timekpr-gui
   The user interface (gtk)

Note: Both executables require administrator/root privileges.

MODULES
-------

1. timekprpam.py - Custom parser for time.conf and
   access.conf

2. timekprcommon.py - Contains common defs shared among the
   timekpr applications.

DESCRIPTION
-----------

timekpr is a useful tool with which an administrator can
limit the daily usage of the computer, either by access 
duration or limiting by access hours each day.

The timekpr daemon/service does a round every 45 seconds 
(default) and checks for accounts that:

- should be unlocked

- passed their daily access duration limit and should 
  be locked and logged out

- passed their allowed hours limit and should be locked 
  and logged out

DEPENDENCIES
------------

timekpr depends on:

1. python >= 2.5

#. libnotify-bin

#. python-gtk2 and python-glade2

#. commands: ps

#. Linux-PAM time and access modules, enabled in:

  - /etc/pam.d/gdm

  - /etc/pam.d/login

6. Special timekpr sections (for now) in:

  - /etc/security/time.conf

  - /etc/security/access.conf

  Sections start with "## TIMEKPR START" and end with
  "## TIMEKPR END".

FILES
-----

/etc/timekpr.conf
  Global timekpr variables, such as directories and grace
  period variables.
/etc/timekpr/
  Folder; per user settings (for login access duration and 
  .lock files).
/usr/share/timekpr/
  Shared folder; timekpr support files.
/usr/share/python-support/timekpr/
  Shared folder; timekpr python support files, executables 
  and modules.
/var/lib/timekpr/
  Folder; per user daemon runtime files (.time, .logout and
  .late).

TODO
----

- Support KDE and XFCE desktop managers

- Use timekpr-client to properly notify the users

- Code (executables and modules) clean-up to match the Python 
  standards.

CONTRIBUTORS
------------

In branch, see: CONTRIBUTORS.txt
or if installed, see: /usr/share/doc/timekpr/CONTRIBUTORS.txt

LEGAL
-----

In branch, see: COPYRIGHT.txt
or if installed, see: /usr/share/doc/timekpr/COPYRIGHT.txt

:Author: vicedar@gmail.com
:Date: 2008-10-27
:Copyright: GNU FDL
:Version: 0.2.0
