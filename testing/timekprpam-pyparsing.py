# Check out:
# - http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION007600000000000000000
# - http://pyparsing.wikispaces.com/message/view/home/7002417

from pyparsing import *
import re

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
tconf_commonops = "&|"
# Negation
tconf_negation = Optional("!", "allow") # block or allow
tconf_negation.setParseAction(tconf_negation_replace)
# days of week and time of day
daysofweek = Group(OneOrMore(Literal("Mo") | Literal("Tu") | Literal("We") | Literal("Th") | Literal("Fr") | Literal("Sa") | Literal("Su") | Literal("Wk") | Literal("Wd") | Literal("Al")))
timeofday = Group(Word(nums,exact=4) + Suppress("-") + Word(nums,exact=4))
tconf_time = tconf_negation + daysofweek + timeofday
tconf_time_list = Group(tconf_time) + Optional(Word(tconf_commonops))
tconf_time_parse = OneOrMore(tconf_time_list) + LineEnd()

# input string
data = """
#xsh ; ttyp* ; root ; !WeMo1700-2030 | !WeFr0600-0830 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0000-2400 # Added by timekpr
xsh & login;ttyp*;root | moot;WdMo0000-2400 | Tu0800-2400 # Added by timekpr
xsh & login ; ttyp* ; root | moot;!WdMo0700-1500 & !MoWeFr1500-2000 # Added by timekpr
a;o; a; e
  

"""

# Ignore commented lines (start with #) and match the ones that have "# Added by timekpr"
matches = re.compile('^[^#]*?([^;]+)# Added by timekpr.*$', re.M).findall(data)

for item in matches:
    print(item)
    result = tconf_time_parse.parseString(item)
    print(result)

#access.conf
#===========

print("\n\naccess.conf\n")

data2 = """
# testing # Added by timekpr
- : lala : ALL # Added by timekpr
-:lala:ALL # Added by timekpr
- : nana123_a : ALL # Added by timekpr
- : testing : ALL # test
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
aconf_action = Word("-+", exact=1)
aconf_action.setParseAction(aconf_action_replace)
aconf_who = Word(alphanums + "_*() ")
aconf_who.setParseAction(aconf_strip_whitespace)
aconf_from = Regex(".*")
aconf_from.setParseAction(aconf_strip_whitespace)
aconf_access_parse = aconf_action + aconf_splitchar + aconf_who + aconf_splitchar + aconf_from

# Ignore commented lines (start with #) and match the ones that have "# Added by timekpr"
matches2 = re.compile('^([^#]+)# Added by timekpr.*$', re.M).findall(data2)

for item in matches2:
    print(item)
    result = aconf_access_parse.parseString(item)
    print(result)

