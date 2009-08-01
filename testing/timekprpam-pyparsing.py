# Check out:
# - http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION007600000000000000000
# - http://pyparsing.wikispaces.com/message/view/home/7002417

from pyparsing import *
import re

#common
#======

# We have to check for other active lines/limitations that might interfere with timekpr
def pre_check_line(line):
    """ Pre-checks the line
        Returns:
            0 = active line, with "# Added by timekpr"
            1 = active line, without "# Added by timekpr"
            2 = ignore this line
    """
    # Ignore whitespace-only line
    if re.search("\s*$", line):
        return 2
    # timekpr lines have "# Added by timekpr" in the end
    if line[-18::] != "# Added by timekpr":
        return 0
    return 1

#time.conf
#===========

print("time.conf\n")

# define grammar
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
tconf_time_parse = Suppress(Regex("(?:.*;){3}")) + OneOrMore(tconf_time_list) + Suppress(Regex("# Added by timekpr")) + LineEnd()

# input string
data = """
#xsh ; ttyp* ; root ; !WeMo1700-2030 | !WeFr0600-0830 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0000-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0200-1500
xsh & login;ttyp*;root | moot;WdMo0000-2400 | Tu0800-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0700-1500 & !MoWeFr1500-2000 # Added by timekpr
a;o; a; e
  

"""

# Ignore commented lines (start with #)
matches_tconf = re.compile('^(?!\s*#).+', re.M).findall(data)
#matches_tconf = re.compile('^[^#\n]*?([^;]+)# Added by timekpr$', re.M).findall(data)

for line in matches_tconf:
    test = pre_check_line(line)
    if test == 1:
        print(line)
        #match_line = re.compile('^.*?([^;]+)# Added by timekpr$').match(line)
        #result = tconf_time_parse.parseString(match_line.group(1))
        result = tconf_time_parse.parseString(line)
        print(result)
    elif test == 0:
        print("WARNING: Unrecognized active line found: %s" % (line))
    # if test == 2, just ignore it

#access.conf
#===========
# Define grammar
# permission (+ or -) : users : origins


print("\n\naccess.conf\n")

data2 = """
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
aconf_access_parse = aconf_permission + aconf_splitchar + aconf_users + aconf_splitchar + aconf_origins

# Ignore commented lines (start with #)
matches_aconf = re.compile('^(?!\s*#).+', re.M).findall(data2)

for line in matches_aconf:
    if pre_check_line(line):
        print(line)
        result = aconf_access_parse.parseString(line)
        print(result)
    else:
        print("WARNING: Unrecognized active line found: %s" % (line))

