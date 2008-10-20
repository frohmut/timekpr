
for developpers
===============

currently the project REQUIRES python >= 2.5

I was new to bazaar and launch pad. this is a reminder to myself and might prove useful for others as well

install bazaar :
I'm on fedora
#yum install bzr

get a working copy of the project

bzr whoami "Nicolas Laurance <nlaurance@zindep.com>"
bzr launchpad-login nlaurance
bzr branch lp:timekpr
cd timekpr

do some editing ...

bzr ci -m"testing bazar checkin" 
Committing to: /home/.../timekpr/
modified TODO
Committed revision 112.

then push back to launchpad

bzr push lp:/timekpr

should definitely work on branch
