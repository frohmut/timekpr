#!/usr/bin/env python
import re
from uuid import uuid4 as uuidrand
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
	#returns format 'ABC1234'
	a = uuidrand().hex.upper()
	letters = re.findall('[A-Z]',a)
	al = choice(letters)*3
	digits = re.findall('\d',a)
	ad = choice(digits)*4
	ticket = al + ad

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
