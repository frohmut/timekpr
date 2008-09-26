#!/usr/bin/env python
import re
from time import strftime

#TODO: Test and make it a module

## Check/enable/disable to /etc/pam.d/gdm and /etc/pam.d/login

## COMMON
def getconfsection(conffile):
	#Argument: string
	#Returns the section of the timekpr in a file
	s = open(conffile).read()
	m = re.compile('## TIMEKPR START\n(.*)\n## TIMEKPR END', re.S).findall(s)
	if len(m) > 1: exit('Error: More then one timekpr sections found(?): "' + conffile + '"')
	return m[0]

## Read/Write access.conf
def parseaccessconf(f = '/etc/security/access.conf'):
	#Parses the timekpr section in access.conf
	#Returns a list with the disabled usernames: ['niania','wawa']
	s = getconfsection(f)
	m = re.compile('^-:([^:]+):ALL$',re.M).findall(s)
	#If no matches (or bad format?), m = []
	return m

def isuserlocked(u):
	#Argument: username
	#Checks if user is in access.conf
	#Returns: True/False
	try: i = parseaccessconf().index(u)
	except ValueError: i = -1
	if i < 0: return False
	return True

def unlockuser(u, f = '/etc/security/access.conf'):
	#Argument: username
	#Removes access.conf line of user
	#Returns True (even if user is not locked) or False (if not possible)
	if isuserlocked(u) is False: return True
	fn = open(f,'w+')
	s = fn.read()
	m = re.sub('(## TIMEKPR START\n.*)-:'+u+':ALL\n','\\1', s)
	try: fn.write(m)
	except: return False
	fn.close()
	return True

def lockuser(u, f = '/etc/security/access.conf'):
	#Argument: username
	#Removes access.conf line of user
	#Returns True (even if user is already locked) or False
	if isuserlocked(u) is True: return True
	fn = open(f,'w+')
	s = fn.read()
	m = re.sub('(## TIMEKPR END.*)', '-:'+u+':ALL\n\\1', s)
	try: fn.write(m)
	except: return False
	fn.close()
	return True

## Read/write time.conf
def hourize(n):
	#make 7 into 0700, or 22 into 2200
	if int(n) < 10: return '0%s00' % str(n)
	return '%s00' % str(n)

def converttimeline(hfrom,hto):
	#all same:
	mfrom = re.compile('^(?:(\d+) ){6}\\1').findall(' '.join(hfrom))
	mto = re.compile('^(?:(\d+) ){6}\\1').findall(' '.join(hto))
	#return Al0700-2400
	if mfrom and mto: return 'Al' + hourize(mfrom[0]) + '-' + hourize(mto[0])
	
	#or separately all days
	su = 'Su' + hourize(hfrom[0]) + '-' + hourize(hto[0])
	mo = 'Mo' + hourize(hfrom[1]) + '-' + hourize(hto[1])
	tu = 'Tu' + hourize(hfrom[2]) + '-' + hourize(hto[2])
	we = 'We' + hourize(hfrom[3]) + '-' + hourize(hto[3])
	th = 'Th' + hourize(hfrom[4]) + '-' + hourize(hto[4])
	fr = 'Fr' + hourize(hfrom[5]) + '-' + hourize(hto[5])
	sa = 'Sa' + hourize(hfrom[6]) + '-' + hourize(hto[6])
	#Escaping \|, will be used in regular expressions
	return ' \| '.join([su,mo,tu,we,th,fr,sa])

def mktimeconfline(uname,hfrom,hto): return '\*;\*;'+uname+';'+converttimeline(hfrom,hto) #Escaping \*, will be used in regular expressions
""" Example:
hfrom = ['7', '7', '7', '7', '7', '7', '7']
hto = ['22', '22', '22', '22', '22', '22', '22']
mktimeconfline("username",hfrom,hto)
"""

def adduserlimits(username,bftom,bto,f = '/etc/security/time.conf'):
	#Adds a line with the username and their time limits in time.conf
	#Returns True or False (if it can't write to file)
	line = mktimeconfline(username,bfrom,bto)
	fn = open(f,'w+')
	s = fn.read()
	m = re.sub('(## TIMEKPR END.*)',line+'\n\\1', s)
	try: fn.write(m)
	except: return False
	fn.close()
	return True

def removeuserlimits(username,f = '/etc/security/time.conf'):
	#Removes a line with the username in time.conf
	#Returns True or False (if it can't write to file)
	fn = open(f,'w+')
	s = fn.read()
	m = re.sub('(## TIMEKPR START\n.*)\*;\*;'+username+'\n','\\1', s)
	try: fn.write(m)
	except: return False
	fn.close()
	return True

def isuserlimited(u,f = '/etc/security/time.conf'):
	#Argument: username
	#Checks if user is in time.conf
	#Returns: True/False
	s = getconfsection(f)
	m = re.compile('^\*;\*;([^;]+);',re.M).findall(s)
	try: i = m.index(u)
	except ValueError: i = -1
	if i < 0: return False
	return True

def isuserlimitednow(u,f = '/etc/security/time.conf'):
	#Argument: username
	#Checks if username should be limited as defined in time.conf
	#If this is True and the user is logged in, they should be killed
	#Returns: True or False (even if user is not in time.conf)
	if isuserlimited(u) is False: return False
	s = getconfsection(f)
	m = re.compile('^\*;\*;'+u+';(.*)$',re.M).findall(s)
	
	today = int(time.strftime("%w"))
	hournow = int(time.strftime("%H"))
	
	#If Al (All days):
	x = re.match('Al(\d\d)00-(\d\d)00',m[0])
	if x:
		low = int(x.group(1)) #lowest limit
		high= int(x.group(2)) #highest limit
		if low <= hournow < high: return False
	else:
		d = re.split(' \| ',m[0])[today]
		z = re.match('\w\w(\d\d)00-(\d\d)00',d)
		low = int(z.group(1))
		high = int(z.group(2))
		if low <= hournow < high: return False
	return True

def strint(x): return str(int(x)) #makes '08' into '8' and '10' as '10'

def converttconf(tfrom,tto,mode=0):
	""" In short, it removes the unnecessary 0 and multiplies tfrom,tto if necessary
	If mode=0 (default), it converts tfrom = ['08','08','13','14','15','01','09'], tto = ['22','14','19','20','21','23','25'] into ['8','8','13','14','15','1','9'] and ['22','14','19','20','21','23','25'] respectively
	If mode=1, it converts tfrom = '08', tto = '22' into ['8','8','8','8','8','8','8'] and ['22','22','22','22','22','22','22'] respectively
	"""
	if mode == 0:
		ffrom = map(strint,tfrom)
		fto = map(strint,tto)
	elif mode == 1:
		#Single values mode, need to multiply 7 times
		ffrom = [strint(tfrom)]*7
		fto = [strint(tto)]*7
	return ffrom,fto

def parsetimeconf(f = '/etc/security/time.conf'):
	#Returns a list with usernames and from/to configurations from the time.conf file
	c = getconfsection(f)
	utlist = re.compile('^\*;\*;([^;]+);(.*)$', re.M).findall(c)
	return utlist
	#example: [('niania', 'Al0000-2400'),('wawa', 'Su0700-2200 | Mo0700-2200 | Tu0700-2200 | We0700-2200 | Th0700-2200 | Fr0700-2200 | Sa0900-2200')]

def parseutlist(utlist):
	#Parses the list from parsetimeconf()
	retlist = []
	for u,t in utlist:
		#('niania', 'Al0000-2400')
		#u = 'niania' and t = 'Al0000-2400'
		
		#Check if Al is used
		checkAl = re.compile('^Al(\d{2})00-(\d{2})00$').findall(t)
		if checkAl:
			final = converttconf(checkAl[0][0],checkAl[0][1],1)
		else:
			#Break time in pieces
			pieces = re.split(' \| ',t)
			if len(pieces) != 7: exit('Error: Unsupported format detected (should have 7 time items): "' + t + '"')
			if not re.search('^Su\d{2}00-\d{2}00$',pieces[0]): exit('Error: Unsupported format detected (Sunday should be first): "' + t + '"')
			#0=Sunday, su[0] is from, su[1] is to
			su = re.compile('^Su(\d\d)00-(\d\d)00$').findall(pieces[0])[0]
			mo = re.compile('^Mo(\d\d)00-(\d\d)00$').findall(pieces[1])[0]
			tu = re.compile('^Tu(\d\d)00-(\d\d)00$').findall(pieces[2])[0]
			we = re.compile('^We(\d\d)00-(\d\d)00$').findall(pieces[3])[0]
			th = re.compile('^Th(\d\d)00-(\d\d)00$').findall(pieces[4])[0]
			fr = re.compile('^Fr(\d\d)00-(\d\d)00$').findall(pieces[5])[0]
			sa = re.compile('^Sa(\d\d)00-(\d\d)00$').findall(pieces[6])[0]
			final = converttconf([su[0],mo[0],tu[0],we[0],th[0],fr[0],sa[0]],[su[1],mo[1],tu[1],we[1],th[1],fr[1],sa[1]])
		retlist.append((u,final))
		#Append example:
		#user: [niania,(['0', '0', '0', '0', '0', '0', '0'], ['24', '24', '24', '24', '24', '24', '24'])]
		#user: [wawa,(['7', '7', '7', '7', '7', '7', '9'], ['22', '22', '22', '22', '22', '22', '22'])]
	return retlist
	"""Returns a list (retlist):
	[0] = first item:
		[0] = username niania
		[1] = fromto:
			[0] = from ['0', '0', '0', '0', '0', '0', '0']
			[1] = to ['24', '24', '24', '24', '24', '24', '24']
	Example: parseutlist(utlist)[0][1][0]
		['0', '0', '0', '0', '0', '0', '0']
	"""
