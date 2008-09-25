#!/usr/bin/env python
import re

#TODO: Test and make it a module

## Check/enable/disable to /etc/pam.d/gdm and /etc/pam.d/login

## Read access.conf
def parseaccessconf(conffile = '/etc/security/access.conf'):
	c = open('/etc/security/access.conf').read()
	#We don't support some stuff yet
	if re.search('^[+-].*:\s?(?!ALL)$',c,re.M): exit('Error: The program does not support other than "ALL" yet: "'+i+'"')
	if re.search('^[+-]\s?:\s?[^:]*[\(\)][^:]*\s?:\s?(?!ALL)$',c,re.M): exit('Error: The program does not support groups yet: "'+i+'"')
	
	#Currently supports "- : username : ALL" or "+ : username : ALL"
	ualist = re.compile('^-\s?:\s?([^:]*)\s?:\s?ALL$', re.M).findall(c)
	"""ualist:
		permit: allow(+) or deny(-)
		user
		type of block
	"""

## Convert timekpr format into a time.conf line
def hourize(n):
	#make 7 into 0700, or 22 into 2200
	if int(n) < 10: return '0%s00' % str(n)
	return '%s00' % str(n)

def optimizetimeline(hfrom,hto):
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
	return ' | '.join([su,mo,tu,we,th,fr,sa])

def mktimeconfline(uname,hfrom,hto): return '*;*;'+uname+';'+optimizetimeline(hfrom,hto)
""" Example:
hfrom = "7 7 7 7 7 7 7".split(" ")
hto = "22 22 22 22 22 22 22".split(" ")
mktimeconfline("username",hfrom,hto)
"""

## Attempt to read time.conf an return it in a timekpr format
def strint(x): return str(int(x)) #makes '08' into '8' and '10' as '10'

def converttconf(tfrom,tto,mode=0):
	"""
	In short, it removes the unnecessary 0 and multiplies tfrom,tto if necessary
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

def parsetimeconf(conffile = '/etc/security/time.conf'):
	#Returns an array/list with usernames and from/to configurations from the time.conf file
	c = open(conffile).read()
	#TODO: Remove the '#' from the regex string when done testing
	utlist = re.compile('^#\*;\*;([^;]+);(.*)$', re.M).findall(c)
	return utlist
	#example: [('niania', 'Al0000-2400'),('wawa', 'Su0700-2200 | Mo0700-2200 | Tu0700-2200 | We0700-2200 | Th0700-2200 | Fr0700-2200 | Sa0900-2200')]

def parseutlist(utlist):
	#Parses the list from parsetimeconf()
	retlist = []
	for u,t in utlist:
		#('niania', 'Al0000-2400')
		#u = 'niania' and t = 'Al0000-2400'
		
		#Some stuff not supported yet
		if re.search('!',t): exit('Error: The program does not support "!" negation yet: "' + t + '"')
		if re.search('&',t): exit('Error: The program does not support "&" adding yet: "' + t + '"')
		if re.search('[A-Za-z]{3,}',t): exit('Error: The program does not support same setting for a lot of days together yet: "' + t + '"')
		#Check if Al is used
		if re.search('^Al\d{4}-\d{4}$',t) and not re.search('^Al\d{2}00-\d{2}00$',t): exit('Error: The program does not support minutes yet: "' + t + '"')
		checkAl = re.compile('^Al(\d{2})00-(\d{2})00$').findall(t)
		if checkAl:
			final = converttconf(checkAl[0][0],checkAl[0][1],1)
		else:
			#Break time in pieces
			pieces = re.split(' \| ',t)
			if len(pieces) != 7: exit('Error: Unsupported format detected (should have 7 time items): "' + t + '"')
			if not re.search('^Su\d{2}00-\d{2}00$',pieces[0]): exit('Error: Unsupported format detected (Sunday should be first): "' + t + '"')
			#Analyze each piece separately
			for i in pieces:
				if re.search('Al|Wk|Wd',i): exit('Error: The program does not support Al or Wk or Wd alone or with other days yet: "' + i + '"')
				if not re.search('^[A-Z][a-z]\d{2}00-\d{2}00$',i): exit('Error: Unsupported format detected: "' + i + '"' + ' at line: "' + t + '" (program supports hours only, not minutes)')
			#Wheow, now let's parse it properly
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
	"""Returns a list:
	retlist
	[0] item:
		[0] = username niania
		[1] = fromto:
			[0] = from ['0', '0', '0', '0', '0', '0', '0']
			[1] = to ['24', '24', '24', '24', '24', '24', '24']
	Example: parseutlist(utlist)[0][1][0]
		['0', '0', '0', '0', '0', '0', '0']
	"""




""" the syntax of the lines is as follows:
#
#       services;ttys;users;times
#
# white space is ignored and lines maybe extended with '\\n' (escaped
# newlines). As should be clear from reading these comments,
# text following a '#' is ignored to the end of the line.
#
# the combination of individual users/terminals etc is a logic list
# namely individual tokens that are optionally prefixed with '!' (logical
# not) and separated with '&' (logical and) and '|' (logical or).
#
# services
#	is a logic list of PAM service names that the rule applies to.
#
# ttys
#	is a logic list of terminal names that this rule applies to.
#
# users
#	is a logic list of users or a netgroup of users to whom this
#	rule applies.
#
# NB. For these items the simple wildcard '*' may be used only once.
#
# times
#	the format here is a logic list of day/time-range
#	entries the days are specified by a sequence of two character
#	entries, MoTuSa for example is Monday Tuesday and Saturday. Note
#	that repeated days are unset MoMo = no day, and MoWk = all weekdays
#	bar Monday. The two character combinations accepted are
#
#		Mo Tu We Th Fr Sa Su Wk Wd Al
#
#	the last two being week-end days and all 7 days of the week
#	respectively. As a final example, AlFr means all days except Friday.
#
#	each day/time-range can be prefixed with a '!' to indicate "anything
#	but"
#
#	The time-range part is two 24-hour times HHMM separated by a hyphen
#	indicating the start and finish time (if the finish time is smaller
#	than the start time it is deemed to apply on the following day).
#
# for a rule to be active, ALL of service+ttys+users must be satisfied
# by the applying process.
"""

