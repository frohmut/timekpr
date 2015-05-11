.. Manual page for timekpr daemon
.. Can be converted using manpage-writer (sandbox at docutils website)
.. This document is written in rst.
.. Reference: http://docutils.sf.net/docs/user/rst/quickref.html
.. man-pages can have these parts:
..   NAME
..   SYNOPSIS
..   CONFIGURATION	  [Normally only in Section 4]
..   DESCRIPTION
..   OPTIONS.. [Normally only in Sections 1, 8]
..   EXIT STATUS		[Normally only in Sections 1, 8]
..   RETURN VALUE	   [Normally only in Sections 2, 3]
..   ERRORS..  [Typically only in Sections 2, 3]
..   ENVIRONMENT
..   FILES
..   VERSIONS		   [Normally only in Sections 2, 3]
..   CONFORMING TO
..   NOTES
..   BUGS
..   EXAMPLE
..   SEE ALSO

=========
 timekpr
=========

------------------------------
Keep control of computer usage
------------------------------

:Author: vicedar@gmail.com
:Date: 2008-10-27
:Copyright: GNU FDL
:Version: 0.2.0
:Manual section: 1
:Manual group: administration

SYNOPSIS
========

``invoke-rc.d`` ``timekpr`` [ status | start | stop | restart ]

DESCRIPTION
===========

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
