#!/usr/bin/env python
import re
from random import choice
from glob import glob
from os.path import isfile

# timekpr ticketing system
# Could be used to grant tickets with a specific time length
# Useful when the administrator is not there
# NOTE: This cannot be used when the user is not logged in
#   (Linux-PAM time.conf and access.conf would block them entirely from logging in)

TKTDIR = '/etc/timekpr'
TKTFILE = TKTDIR + '/' + '.tickets'
#.tickets file format:
#username length(seconds) ticketid

def mkticket():
	#Create a ticketid
	#returns format 'ABC-1234'
	letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')*4
	al = choice(letters) + choice(letters) + choice(letters)
	digits = list('0123456789')*6
	ad = choice(digits) + choice(digits) + choice(digits) + choice(digits) + choice(digits)
	ticket = "%s-%s" % (al, ad)
	return ticket

def gettickets(u = ''):
	#Without u argument, returns tickets of all usernames
	f=TKTFILE
	if isfile(f):
		fr = open(f,'r').read()
		if not u: match=re.compile('^([^\s]+) (\d+) (\w+)').findall(fr)
		else: match=re.compile('^('+username+') (\d+) (\w+)').findall(fr)
		#match is a list:
		# item [0] is a list with text strings: ['username', 'lengthseconds', 'ticketid']
		# e.g. match[0][1] is the username
		return match
	return False
