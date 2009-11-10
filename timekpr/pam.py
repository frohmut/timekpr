""" A library timekpr uses to read/edit Linux-PAM configuration files.
    Currently using modules: time, access
    Warning: Not all Linux-PAM possibilities are supported!
"""

#    Copyright (C) 2008-2009 Savvas Radevic <vicedar@gmail.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import re
from time import strftime

# TODO: Check/enable/disable to /etc/pam.d/gdm and /etc/pam.d/login

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
        #       ['24', '24', '24', '24', '24', '24', '24'])]
        # user: [wawa,(['7', '7', '7', '7', '7', '7', '9'], 
        #        ['22', '22', '22', '22', '22', '22', '22'])]
    
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


"""

THESE ARE THE NEW STUFF!!!

"""


""" timekprpam 
    It's a Linux-PAM parser optimized for timekpr and time/access pam modules. 
    In other words, many of the linux-pam capabilities are not supported 
    (and probably will never be!).

    It can currently parse lines that have a comment "# Added by timekpr" at the
    end of the line.

    pyparsing was chosen because it's easier to look at, fix and manipulate
    (compared to simple regular expressions). However, regular expressions are
    still used in this module for simpler tasks.
""" 

# More information on pyparsing:
# - http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION007600000000000000000
# - http://pyparsing.wikispaces.com/message/view/home/7002417

from pyparsing import *
import re
import sys

# =============================================================================
# CLASS: pamparser(type="time.conf", input="file", file="/etc/security/time.conf")
# =============================================================================
#   type    => time.conf or access.conf
#   input   => file (default) or string (for testing)
#   file    => filename (default is blank - if blank, will use default filenames)
#   string  => text string (default is blank)
# Examples? See "TEST"!

class pamparser():
    def __init__(self, type, input="file", file="", string=""):
        # Set default file location if file is not defined
        self.type = type
        self.input = input
        self.file = file
        self.string = string
        self.read_input = ""
        self.result = list()
        self.unrecognized = list()

        self.defaultfiles = {
            "time.conf"   : "/etc/security/time.conf",
            "access.conf" : "/etc/security/access.conf"
        }

        if input == "file" and not file:
            self.file = self.defaultfiles[type]
        elif input == "string" and not string:
            sys.stderr.write("ERROR: pamparser() init: input is 'string' but text string is empty\n")
            sys.exit(1)

        self.active = self.scanActiveLines()
        self.parseLines()
        #self.outputLines()

    # Common
    # ======
    def prepareLine(self, ulist):
        """ Prepare line for writing/output """
        if self.type == "access.conf":
            controldict = { "block": "-", "allow": "+" }
            access = controldict[ulist[0]]
            modified = "%s : %s : %s # Added by timekpr" % (access, ulist[1], ulist[2])
        elif self.type == "time.conf":
            controldict = { "block": "", "allow": "!" }
            # TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: 
            modified = ""
            # Tip: "!" in time.conf means "do not block during this time span" (in other words, "allow")
        return modified

    def appendLine(self, line):
        """ Add a line to self.read_input. Returns the result """
        t = self.read_input.split("\n")
        t.append(line)
        result = "\n".join(t)
        #print(result)
        return result

    def removeLine(self, line):
        """ Removes a line from self.read_input. Returns the result """
        t = self.read_input.split("\n")
        i = t.index(line)
        del t[i]
        result = "\n".join(t)
        #print(result)
        return result

    def writeOutput(self, output):
        """ Writes to file or prints output, depending on the
            input source.
            Arguments:
                text => the text of the whole output
            Returns:
                True => Operation successful
                False => Writing to file failed
        """
        if self.input == "file":
            # output => file
            fr = open(self.file, 'r')
            source = fr.read()
            fr.close()

            # If the output is the same as the original input,
            # don't do anything and return True
            if source == output:
                return True

            try:
                fw = open(self.file, 'w')
                fw.write(output)
                fw.close()
            except IOError:
                return False

        elif self.input == "string":
            # output => print()
            print("OUTPUT: %s" % (output))

        return True # All done!

    def readInput(self):
        """ Read input, file contents or string
            Returns self.read_input
        """
        if self.input == "file":
            try:
                f = open(self.file)
                text = f.read()
                f.close()
            except IOError, e:
                sys.stderr.write("ERROR: pamparser() readInput: %d (%s) Filename: %s\n" % (e.errno, e.strerror, self.file))
                sys.exit(1)
            self.read_input = text
        elif self.input == "string":
            self.read_input = self.string

        return self.read_input

    def scanActiveLines(self):
        # Ignore commented lines (they start with #)
        text = self.readInput()
        result = re.compile('^(?!\s*#).+', re.M).findall(text)
        return result

    def preCheckLine(self, line):
        """ Pre-checks the line
            Returns:
                0 = active line, with "# Added by timekpr"
                1 = active line, without "# Added by timekpr"
                2 = ignore this line
        """
        # Ignore whitespace-only line
        if re.match("^\s*$", line):
            return 2
        # timekpr lines have "# Added by timekpr" in the end
        if line[-18::] != "# Added by timekpr":
            return 0
        return 1

    def parseLines(self):
        # TODO: TODO: Check for duplicate lines (= of the same user)
        """ Creates two lists:
            - active (uncommented) lines, that are recognized by timekpr.
            - active but unrecognized lines.

            self.result => [original line from file, resulting parsed list]
            self.unrecognized => unrecognized lines list
        """
        for line in self.active:
            test = self.preCheckLine(line)

            if test == 1:
                if self.type == "time.conf":
                    tconf_parse = self.time_conf_parser()
                    result = tconf_parse.parseString(line)
                elif self.type == "access.conf":
                    aconf_parse = self.access_conf_parser()
                    result = aconf_parse.parseString(line)
                self.result.append([line, result])

            elif test == 0:
                self.unrecognized.append(line)

            #elif test == 2: just ignore it

    def outputLines(self):
        """ Print active lines and unrecognized active lines.
            Useful for testing purposes.
        """
        for line in self.result:
            print("%s => %s" % (line[0], line[1]))

        if self.unrecognized:
            list_string = "\n".join(self.unrecognized)
            print("\nWARNING: Unrecognized active lines found:\n%s" % (list_string))

    def getActiveLines(self):
        """ Return the self.result list """
        a = self.result
        return a

    def getUnrecognizedLines(self):
        """ Return the self.unrecognized list """
        if self.unrecognized:
            list_string = "\n".join(self.unrecognized)
            print("WARNING: Unrecognized active lines found:\n%s" % (list_string))

    # time.conf
    # =========
    # Define grammar:
    # services;ttys;users;times
    # ! = NOT, & = AND, | = OR
    # * = ANY (can be used only once)

    # Defs
    def tconf_negation_replace(self, s, l, t):
        if t[0] == "!":
            t[0] = "block"
            return t

    def time_conf_parser(self):
        """ time.conf parser.
            Note: Capital-lettered functions are from pyparsing.
        """
        # Common
        tconf_commonops = "&|" # AND/OR
        # Ignore the first two ";"-separated items (services;ttys;users)
        tconf_start = Suppress(Regex("(?:[^;]*;){2}"))

        tconf_users = Regex("[^;]*")
        tconf_users.setParseAction(self.strip_whitespace)

        tconf_splitchar = Suppress(Word(";"))

        # Negation
        tconf_negation = Optional("!", "allow") # block (with "!") or allow (without "!")
        tconf_negation.setParseAction(self.tconf_negation_replace)
        # Days of week
        daysofweek = Group(OneOrMore(Literal("Mo") | Literal("Tu") | Literal("We") | Literal("Th") | Literal("Fr") | Literal("Sa") | Literal("Su") | Literal("Wk") | Literal("Wd") | Literal("Al")))
        # Get the timeofday (4 numbers and "-" and 4 numbers)
        timeofday = Group(Word(nums,exact=4) + Suppress("-") + Word(nums,exact=4))
        # Check negation, the days of week and the time of day
        tconf_time = tconf_negation + daysofweek + timeofday
        # While checking for & or | too
        tconf_time_list = Group(tconf_time) + Optional(Word(tconf_commonops))
        # Do the above all over again once or more times
        tconf_parse = tconf_start + tconf_users + tconf_splitchar + OneOrMore(tconf_time_list) + Suppress(Regex("# Added by timekpr")) + LineEnd()

        return tconf_parse

    # access.conf
    # ===========
    # Define grammar:
    # permission (+ or -) : users : origins

    def aconf_action_replace(self, s, l, t):
        if t[0] == "-":
            t[0] = "block"
            return t
        elif t[0] == "+":
            t[0] = "allow"
            return t

    def strip_whitespace(self, s, l, t):
        return t[0].strip()

    def access_conf_parser(self):
        """ access.conf parser.
            Note: Capital-lettered functions are from pyparsing.
        """
        aconf_splitchar = Suppress(Word(":"))
        # permission - either + or -, 1 character only
        aconf_permission = Word("-+", exact=1)
        aconf_permission.setParseAction(self.aconf_action_replace)
        # users - alphanumeric and one of "_*() " characters
        aconf_users = Word(alphanums + "_*() ")
        aconf_users.setParseAction(self.strip_whitespace)
        # origins - everything else excluding "# Added by timekpr"
        aconf_origins = Regex("[^#]+")
        aconf_origins.setParseAction(self.strip_whitespace)
        aconf_parse = aconf_permission + aconf_splitchar + aconf_users + aconf_splitchar + aconf_origins

        return aconf_parse

# CLASS: timeconf()
# ===================
#  input    => file (default) or string
#  file     => filename (default is /etc/security/time.conf)
#  string   => text string (default is blank)

class timeconf():
    """ Parse time.conf """
    def __init__(self, input="file", file="/etc/security/time.conf", string=""):
        self.input = input
        self.file = file
        self.string = string

        if input == "string" and not string:
            sys.stderr.write("ERROR: timeconf() init: input is 'string' but text string is empty\n")
            sys.exit(1)

        self.parser = pamparser(type="time.conf", input="string", string=self.string)
        self.inputstring = self.parser.readInput()
        self.activelines = self.parser.getActiveLines()

    def test(self):
        for i in self.activelines:
            print(i)

    def parse(self):
        print("moo " + self.file)

# =============================================================================
# CLASS: accessconf()
# =============================================================================
#  input    => file (default) or string
#  file     => filename (default is /etc/security/access.conf)
#  string   => text string (default is blank)

class accessconf():
    """ Parse access.conf """
    def __init__(self, input="file", file="/etc/security/access.conf", string=""):
        self.input = input
        self.file = file
        self.string = string
        self.userdict = dict()

        if input == "string" and not string:
            sys.stderr.write("ERROR: accessconf() init: input is 'string' but text string is empty\n")
            sys.exit(1)

        self.parser = pamparser(type="access.conf", input="string", string=self.string)
        self.inputstring = self.parser.readInput() # the original input text
        self.activelines = self.parser.getActiveLines() # the parsed active lines
        self.createUserDict()

    def createUserDict(self):
        """ Create a new user dictionary. It can return the dictionary.
            Note: It does NOT re-read access.conf

            self.userdict structure: {
                "user": [
                    "original line from input",
                    ["block" or "allow", "user", "origins"]
                ]
            }
        """
        self.userdict.clear()
        for l, i in self.activelines:
            # l = original line, i = parsed list
            # i[1] => user
            # i[0] => status - block or allow
            if not i[1] in self.userdict:
                self.userdict[i[1]] = [l,i]
            else:
                print("WARNING: accessconf() createUserDict(): User %s has more than one active lines: %s" % (i[1], l))

        return self.userdict
        #~ ulist = self.userdict[user][1]      # Get userdict list for the user
        #~ ulist[0] = "allow"                  # Switch "block" to "allow"


    def isuserlocked(self, user):
        """ Checks if user is blocked by access.conf
            Arguments: user  => username
            Returns:
                True  => locked
                False => not locked
        """
        if user in self.userdict: # if user is in access.conf
            ulist = self.userdict[user][1] # Get parsed content
            if ulist[0] == "block": # if user has "block"
                result = True
            else: # has "allow"
                result = False
        else: # if user is not in access.conf
            result = False

        #z = dict({False: "not locked", True: "locked"})
        #print("User: %s Status: %s" % (user, z[result]))
        return result

    def unlockuser(self, user):
        """ Removes access.conf line of user (Unblocks user)
            Arguments: username
            Returns the result of writeOutput():
                True => if unlocked - even if user was already not listed (unlocked)
                False => if writeOutput() failed
        """
        # If user is not locked
        if not self.isuserlocked(user):
            return True

        loriginal = self.userdict[user][0]  # Get original line
        output = self.parser.removeLine(loriginal) # Remove that line
        result = self.parser.writeOutput(output) # Write to output

        return result

    def lockuser(self, user):
        """ Adds access.conf line of user (Blocks user)
            Arguments: username
            Returns the result of writeOutput():
                True => if locked - even if user was already locked
                False => if writeOutput() failed
        """
        # If user is locked
        if self.isuserlocked(user):
            return True

        ulist = ["block", user, "ALL"] # Prepare access data
        line = self.parser.prepareLine(ulist) # Prepare the line
        output = self.parser.appendLine(line) # Add a line
        result = self.parser.writeOutput(output) # Write to output

        return result

    def test(self):
        #print("createUserDict(): %s" % (str(self.createUserDict())))
        #print("isuserlocked(): User lala, result: %d" % (self.isuserlocked("lala")))
        #print("unlockuser(): User lala, result: %s" % (self.unlockuser("lala")))
        print("lockuser(): User papoutsosiko, result: %s" % (self.lockuser("papoutsosiko")))
        pass

# VARIOUS TESTS
# =============
def class_accessconf_test(t):
    accessconf(input="string", string=t).test()

def class_timeconf_test(t):
    timeconf(input="string", string=t).test()

def class_pamparser_test(tconf_test_data, aconf_test_data):
    # CLASS: pamparser()
    # A) time.conf
    testA1 = pamparser(type="time.conf", input="string", string=tconf_test_data)
    print("INFO: - TEST pamparser time.conf A1 (STRING)\n")
    testA1.outputLines()
    #for i1 in testA1.getActiveLines():
    #    print(i1)
    print("\nINFO: - TEST pamparser time.conf A2 (FILE)\n")
    testA2 = pamparser(type="time.conf", input="file")
    testA2.outputLines()

    # B) access.conf
    testB1 = pamparser(type="access.conf", input="string", string=aconf_test_data)
    print("\nINFO: - TEST pamparser access.conf B1 (STRING)\n")
    testB1.outputLines()
    #for i2 in testB1.getActiveLines():
    #    print(i2)
    print("\nINFO: - TEST pamparser access.conf B2 (FILE)\n")
    testB2 = pamparser(type="access.conf", input="file")
    testB2.outputLines()

if __name__ == "__main__":
    tconf_test_data = """
#xsh ; ttyp* ; root ; !WeMo1700-2030 | !WeFr0600-0830 # Added by timekpr
xsh & login ; ttyp* ; ro0_ters;!WdMo0000-2400 # Added by timekpr
    xsh & login ; ttyp* ; root | moot;!WdMo0200-1500
xsh & login;ttyp*;root | moot;WdMo0000-2400 | Tu0800-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0700-1500 & !MoWeFr1500-2000 # Added by timekpr
a;o; a; e
      

    """
    aconf_test_data = """
# testing # Added by timekpr
- : lala : ALL # Added by timekpr
    -:papa4a:ALL # Added by timekpr
- : nana123_a : ALL # Added by timekpr
- : testing : ALL # test
- : testing : ALL EXCEPT root
+ : john : 2001:4ca0:0:101::1# Added by timekpr
+ : root : .foo.bar.org  # Added by timekpr
- : john : 2001:4ca0:0:101::/64 # Added by timekpr
     """

    #class_pamparser_test(tconf_test_data, aconf_test_data)
    #class_timeconf_test(tconf_test_data)
    class_accessconf_test(aconf_test_data)

