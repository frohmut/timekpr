#!/usr/bin/env python
""" A library timekpr uses to read/edit Linux-PAM configuration files.
	Currently using modules: time, access
	Warning: Not all Linux-PAM possibilities are supported!
	Copyright / License: See COPYRIGHT.txt
"""

import re
from time import strftime

#TODO: Check/enable/disable to /etc/pam.d/gdm and /etc/pam.d/login

## COMMON
def getconfsection(conffile):
	"""Returns the content of the timekpr section in a file (access.conf or time.conf)

	Also used to check if the timekpr section is set correctly.
	Arguments: conffile (string)

	"""
	s = open(conffile).read()
	check = re.compile('## TIMEKPR START|## TIMEKPR END').findall(s)
	
	# If the timekpr section lines '## TIMEKPR START' or '## TIMEKPR END' are not
	# found, exit with an error.
	if not len(check):
		exit("Error: Could not find timekpr section in '%s'" % conffile)
	elif len(check) != 2:
		exit("Error: Incorrect format of timekpr section in '%s'" % conffile)
	# Otherwise, get and return the content between the section lines.
	m = re.compile('## TIMEKPR START\n(.*)## TIMEKPR END', re.S).findall(s)
	return m[0]

## Read/Write access.conf
def parseaccessconf(f='/etc/security/access.conf'):
	"""Parses the timekpr section in access.conf

	Returns a list with the (locked) usernames: ['niania','wawa']

	"""
	s = getconfsection(f)
	m = re.compile('^-:([^:\s]+):ALL$', re.M).findall(s)
	#If no matches (or bad format?), m = []
	return m

def isuserlocked(u):
	"""Checks if user is in access.conf

	Argument: username
	Returns: True/False

	"""
	try:
		i = parseaccessconf().index(u)
	except ValueError:
		return False
	return True

def unlockuser(u, f='/etc/security/access.conf'):
	"""Removes access.conf line of user (Unblocks)

	Argument: username
	Returns:
		True (even if user is not listed/locked)
		False (if no write permission)

	"""
	if not isuserlocked(u):
		return True
	fn = open(f, 'r')
	s = fn.read()
	fn.close()
	try:
		fn = open(f, 'w')
	except IOError:
		return False
	m = re.compile('(## TIMEKPR START\n.*)-:' + u + ':ALL\n', re.S).sub('\\1', s)
	fn.write(m)
	fn.close()
	return True

def lockuser(u, f='/etc/security/access.conf'):
	"""Adds access.conf line of user

	timekpr uses access.conf to lock/disable user accounts from logging in.
	Arguments: username
	Returns True (even if user is already locked) or False

	"""
	if isuserlocked(u):
		return True
	fn = open(f, 'r')
	s = fn.read()
	fn.close()
	try:
		fn = open(f, 'w')
	except IOError:
		return False
	m = re.sub('(## TIMEKPR END)', '-:' + u + ':ALL\n\\1', s)
	fn.write(m)
	fn.close()
	return True

## Read/write time.conf
def hourize(n):
	"""Makes integers, e.g. 7 into 0700, or 22 into 2200 - used in converttimeline()"""
	if int(n) < 10:
		return '0%s00' % n
	return '%s00' % n

def converttimeline(hfrom, hto):
	"""Converts a list of hours (from and to limits) into a time.conf line

	Arguments hfrom and hto MUST be lists and text strings inside, e.g.
	 ['0','0','0','0','0','0','0']
	Does NOT support all of the features of time.conf, e.g. negation!

	"""
	if len(hfrom) != 7 or len(hto) != 7:
		exit('Error: converttimeline accepts from-to lists of 7 items each')
	#if all same:
	mfrom = re.compile('^(\d+) \\1 \\1 \\1 \\1 \\1 \\1$').search(' '.join(hfrom))
	mto = re.compile('^(\d+) \\1 \\1 \\1 \\1 \\1 \\1$').search(' '.join(hto))
	#return Al0700-2400
	if mfrom and mto:
		return 'Al' + hourize(mfrom.group(1)) + '-' + hourize(mto.group(1))
	
	#or if all days separate
	su = 'Su' + hourize(hfrom[0]) + '-' + hourize(hto[0])
	mo = 'Mo' + hourize(hfrom[1]) + '-' + hourize(hto[1])
	tu = 'Tu' + hourize(hfrom[2]) + '-' + hourize(hto[2])
	we = 'We' + hourize(hfrom[3]) + '-' + hourize(hto[3])
	th = 'Th' + hourize(hfrom[4]) + '-' + hourize(hto[4])
	fr = 'Fr' + hourize(hfrom[5]) + '-' + hourize(hto[5])
	sa = 'Sa' + hourize(hfrom[6]) + '-' + hourize(hto[6])
	return ' | '.join([su, mo, tu, we, th, fr, sa])


def mktimeconfline(u, hfrom, hto):
	"""Makes the time.conf line - uses converttimeline()

	Example:
		hfrom = ['7', '7', '7', '7', '7', '7', '7']
		hto = ['22', '22', '22', '22', '22', '22', '22']
		mktimeconfline("maria",hfrom,hto)
	Example return:
		'*;*;maria;Al0700-2200'

	"""
	return '*;*;' + u + ';' + converttimeline(hfrom, hto)

def adduserlimits(username, bfrom, bto, f='/etc/security/time.conf'):
	"""Adds a line with the username and their from and to time limits in time.conf

	Arguments: username, bfrom (list), bto (list)
	Returns True or False (if no write permission)

	"""
	getconfsection(f) #Check if timekpr section exists
	line = mktimeconfline(username, bfrom, bto) + "\n"
	fn = open(f, 'r')
	s = fn.read()
	fn.close()
	try:
		fn = open(f, 'w')
	except IOError:
		return False
	m = re.sub('(## TIMEKPR END)', line + '\\1', s)
	fn.write(m)
	return True

def removeuserlimits(username, f='/etc/security/time.conf'):
	"""Removes a line with the username in time.conf

	Returns True or False (if no write permission)

	"""
	getconfsection(f) # Check if timekpr section exists
	fn = open(f, 'r')
	s = fn.read()
	fn.close()
	try:
		fn = open(f, 'w')
	except IOError:
		return False
	m = re.compile('(## TIMEKPR START\n.*)\*;\*;' + username + ';[^\n]*\n', re.S).sub('\\1', s)
	fn.write(m)
	fn.close()
	return True

def isuserlimited(u, f='/etc/security/time.conf'):
	"""Checks if user is in time.conf (if account has limited access hours)

	Argument: username
	Returns: True/False

	"""
	s = getconfsection(f)
	#Check if Al0000-2400 present:
	x = re.compile('^\*;\*;' + u + ';Al0000-2400$', re.M).search(s)
	if x:
		return False
	m = re.compile('^\*;\*;([^;]+);', re.M).findall(s)
	try:
		i = m.index(u)
	except ValueError:
		return False
	return True

def isuserlimitednow(u, f='/etc/security/time.conf'):
	"""Checks if username should be limited as defined in time.conf

	Argument: username
	If this is True and the user is logged in, they should be killed
	Returns: True or False (even if user is not in time.conf)

	"""
	if not isuserlimited(u):
		return False
	s = getconfsection(f)
	m = re.compile('^\*;\*;' + u + ';(.*)$', re.M).findall(s)
	today = int(strftime("%w"))
	hournow = int(strftime("%H"))
	#If Al (All days):
	x = re.match('Al(\d\d)00-(\d\d)00', m[0])
	if x:
		low = int(x.group(1)) #lowest limit
		high= int(x.group(2)) #highest limit
		if low <= hournow < high:
			return False
	else:
		d = re.split(' \| ', m[0])[today]
		z = re.match('\w\w(\d\d)00-(\d\d)00', d)
		low = int(z.group(1))
		high = int(z.group(2))
		if low <= hournow < high:
			return False
	return True

def isuserlimitedtoday(u, f='/etc/security/time.conf'):
	#Argument: username
	#Checks if username has limitations for this day
	#Returns: True or False (even if user is not in time.conf)
	if not isuserlimited(u):
		return False
	s = getconfsection(f)
	m = re.compile('^\*;\*;' + u + ';(.*)$', re.M).findall(s)
	today = int(strftime("%w"))
	#If Al (All days):
	x = re.match('Al0000-2400', m[0])
	if x:
		return False
	else:
		day = { 0:"Su", 1:"Mo", 2:"Tu", 3:"We", 4:"Th", 5:"Fr", 6:"Sa" }
		g = re.compile(day[today] + '0000-2400').search(m[0])
		if g:
			return False
		return True

def strint(x):
	#makes '08' into '8' and '10' as '10'
	return str(int(x))

def converttconf(tfrom, tto, mode=0):
	"""Removes the unnecessary 0 and multiplies from and to lists if necessary

	If mode = 0 (default), it converts tfrom = ['08','08','13','14','15','01','09'], 
	tto = ['22','14','19','20','21','23','25'] into ['8','8','13','14','15','1','9']
	and ['22','14','19','20','21','23','25'] respectively
	If mode = 1, it converts tfrom = '08', tto = '22' into ['8','8','8','8','8','8','8']
	and ['22','22','22','22','22','22','22'] respectively

	WARNING: Will NOT distinguish if tfrom is a list or string if mode is not properly defined!

	"""
	if mode == 0:
		ffrom = list(map(strint, tfrom))
		fto = list(map(strint, tto))
	elif mode == 1:
		#Single values mode, need to multiply 7 times
		ffrom = [strint(tfrom)] * 7
		fto = [strint(tto)] * 7
	return ffrom, fto

def parsetimeconf(f='/etc/security/time.conf'):
	"""Returns a list with usernames with from and to limits from the time.conf file

	Return example:
	[('niania', 'Al0000-2400'), ('wawa', 'Su0700-2200 | Mo0700-2200 | Tu0700-2200 | We0700-2200 | Th0700-2200 | Fr0700-2200 | Sa0900-2200')]

	"""
	c = getconfsection(f)
	utlist = re.compile('^\*;\*;([^;]+);(.*)$', re.M).findall(c)
	return utlist

def parseutlist(utlist):
	"""Parses the list from parsetimeconf()

	Example: ['niania', 'Al0000-2400']
	Returns a list (retlist):
		[0] = first item:
			[0] = username niania
			[1] = fromto:
				[0] = from ['0', '0', '0', '0', '0', '0', '0']
				[1] = to ['24', '24', '24', '24', '24', '24', '24']
	Example usage:
		parseutlist(utlist)[0][1][0]
		['0', '0', '0', '0', '0', '0', '0']

	"""
	retlist = []
	for u,t in utlist:
		#Check if Al is used
		checkAl = re.compile('^Al(\d{2})00-(\d{2})00$').search(t)
		if checkAl:
			final = converttconf(checkAl.group(1), checkAl.group(2), 1)
		else:
			pieces = re.split(' \| ', t) #Break time in 'pieces'
			if len(pieces) != 7:
				exit('Error: Unsupported format detected (should have 7 time items): "%s"' % t)
			if not re.search('^Su\d{2}00-\d{2}00$', pieces[0]):
				exit('Error: Unsupported format detected (Sunday should be first): "%s"' % t)
			#0=Sunday, su[0] is from, su[1] is to
			restr = '^%s(\d\d)00-(\d\d)00$'
			su = re.compile(restr % 'Su').findall(pieces[0])[0]
			mo = re.compile(restr % 'Mo').findall(pieces[1])[0]
			tu = re.compile(restr % 'Tu').findall(pieces[2])[0]
			we = re.compile(restr % 'We').findall(pieces[3])[0]
			th = re.compile(restr % 'Th').findall(pieces[4])[0]
			fr = re.compile(restr % 'Fr').findall(pieces[5])[0]
			sa = re.compile(restr % 'Sa').findall(pieces[6])[0]
			final = converttconf([su[0], mo[0], tu[0], we[0], th[0], fr[0], sa[0]], \
								[su[1], mo[1],tu[1],we[1],th[1],fr[1],sa[1]])
		retlist.append([u, final])
		# Internal example - retlist.append appends like so:
		# user: [niania,(['0', '0', '0', '0', '0', '0', '0'], 
		#	   ['24', '24', '24', '24', '24', '24', '24'])]
		# user: [wawa,(['7', '7', '7', '7', '7', '7', '9'], 
		#		['22', '22', '22', '22', '22', '22', '22'])]
	
	return retlist

def getuserlimits(u):
	"""Gets user from-to time limitations defined in time.conf

	Argument: username
	Return example:
		[0] = from ['0', '0', '0', '0', '0', '0', '0']
		[1] = to ['24', '24', '24', '24', '24', '24', '24']

	"""
	bf = ['0', '0', '0', '0', '0', '0', '0']
	bt =  ['24', '24', '24', '24', '24', '24', '24']
	ls = parseutlist(parsetimeconf())
	for user, [bfrom, bto] in ls:
		if u == user:
			return [bfrom, bto]
	return [bf, bt]

