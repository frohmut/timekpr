""" timekprpam 
    It's a Linux-PAM parser optimized for timekpr and time/access pam modules. 
    In other words, many of the linux-pam capabilities are not supported 
    (and probably will never be!).

    It can currently parse lines that have a comment "# Added by timekpr" at the
    end of the line (and that aren't comments).

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

# common
# ======

# Ignore commented lines (start with #)
def confGetActiveLines(text):
    result = re.compile('^(?!\s*#).+', re.M).findall(text)
    return result

def confPreCheckLine(line):
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

def confOutputLines(match, conf):
    """ Outputs lines and checks for unrecognized ones (not controlled by timekpr)
        Required arguments: matched lines, conf type ("time" or "access")
    """
    unrecognized_lines = list()
    for line in match:
        test = confPreCheckLine(line)
        if test == 1:
            if conf == "time":
                result = tconf_parse.parseString(line)
            elif conf == "access":
                result = aconf_parse.parseString(line)
            print("%s\n%s" % (line, result))
        elif test == 0:
            unrecognized_lines.append(line)
        #elif test == 2: just ignore it

    if unrecognized_lines:
        string = "\n".join(unrecognized_lines)
        print("\nWARNING: Unrecognized active lines found:\n%s" % (string))

# time.conf
# =========
# Define grammar
# services;ttys;users;times
# ! = NOT, & = AND, | = OR
# * = ANY (can be used only once)

# Required - grammar for the times limitation

# Defs
def tconf_negation_replace(s, l, t):
    if t[0] == "!":
        t[0] = "block"
        return t

# Common
tconf_commonops = "&|" # AND/OR
# Ignore the first three ";"-separated items (services;ttys;users)
tconf_start = Suppress(Regex("(?:.*;){3}"))
# Negation
tconf_negation = Optional("!", "allow") # block (with "!") or allow (without "!")
tconf_negation.setParseAction(tconf_negation_replace)
# Days of week
daysofweek = Group(OneOrMore(Literal("Mo") | Literal("Tu") | Literal("We") | Literal("Th") | Literal("Fr") | Literal("Sa") | Literal("Su") | Literal("Wk") | Literal("Wd") | Literal("Al")))
# Get the timeofday (4 numbers and "-" and 4 numbers)
timeofday = Group(Word(nums,exact=4) + Suppress("-") + Word(nums,exact=4))
# Check negation, the days of week and the time of day
tconf_time = tconf_negation + daysofweek + timeofday
# While checking for & or | too
tconf_time_list = Group(tconf_time) + Optional(Word(tconf_commonops))
# Do the above all over again once or more times
tconf_parse = tconf_start + OneOrMore(tconf_time_list) + Suppress(Regex("# Added by timekpr")) + LineEnd()

# access.conf
# ===========
# Define grammar
# permission (+ or -) : users : origins

def aconf_action_replace(s, l, t):
    if t[0] == "-":
        t[0] = "block"
        return t
    elif t[0] == "+":
        t[0] = "allow"
        return t

def aconf_strip_whitespace(s, l, t):
    return t[0].strip()

aconf_splitchar = Suppress(Word(":"))
# permission - either + or -, 1 character only
aconf_permission = Word("-+", exact=1)
aconf_permission.setParseAction(aconf_action_replace)
# users - alphanumeric and one of "_*() " characters
aconf_users = Word(alphanums + "_*() ")
aconf_users.setParseAction(aconf_strip_whitespace)
# origins - everything else excluding "# Added by timekpr"
aconf_origins = Regex("[^#]+")
aconf_origins.setParseAction(aconf_strip_whitespace)
aconf_parse = aconf_permission + aconf_splitchar + aconf_users + aconf_splitchar + aconf_origins

# Test data
# =========

# time.conf
print("time.conf\n")

tconf_test_data = """
#xsh ; ttyp* ; root ; !WeMo1700-2030 | !WeFr0600-0830 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0000-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0200-1500
xsh & login;ttyp*;root | moot;WdMo0000-2400 | Tu0800-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0700-1500 & !MoWeFr1500-2000 # Added by timekpr
a;o; a; e
  

"""

matches_tconf = confGetActiveLines(tconf_test_data)
confOutputLines(matches_tconf, "time")

# access.conf
print("\n\naccess.conf\n")

aconf_test_data = """
# testing # Added by timekpr
- : lala : ALL # Added by timekpr
-:lala:ALL # Added by timekpr
- : nana123_a : ALL # Added by timekpr
- : testing : ALL # test
- : testing : ALL EXCEPT root
+ : john : 2001:4ca0:0:101::1# Added by timekpr
+ : root : .foo.bar.org  # Added by timekpr
- : john : 2001:4ca0:0:101::/64 # Added by timekpr
"""

matches_aconf = confGetActiveLines(aconf_test_data)
confOutputLines(matches_aconf, "access")
