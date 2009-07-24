# Check out:
# - http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION007600000000000000000
# - http://pyparsing.wikispaces.com/message/view/home/7002417

from pyparsing import *
import re

## time.conf
# define grammar
# services;ttys;users;times
# ! = NOT, & = AND, | = OR
# * = ANY (can be used only once)

# Not required - grammar for parsing the whole line
# xsh & login ; ttyp* ; root | moot;!WdMo0000-2400 & !Tu0800-2400 # Added by timekpr
#tconf_splitchar = Suppress(";")
#tconf_commonchars = "*!"
#tconf_commonops = "&|"
#tconf_services = OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops)))
#tconf_ttys = OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops)))
#tconf_users = OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops)))
#tconf_times = OneOrMore(Word(alphanums + tconf_commonchars + "-") + Optional(Word(tconf_commonops)))
#tconf_comment = Optional(Combine(Suppress(Word("#")) + Regex(".*")))
#tconf_line_parse = LineStart() + Group(tconf_services) + tconf_splitchar + Group(tconf_ttys) + tconf_splitchar + Group(tconf_users) + tconf_splitchar + Group(tconf_times) + tconf_comment + LineEnd()

# Required - grammar for the times limitation

# Defs
def negation_replace(s, l, t):
    if t[0] == "!":
        t[0] = "block"
        return t

# Common
tconf_commonops = "&|"
# Negation
negation = Optional("!", "allow") # block or allow
negation.setParseAction(negation_replace)
# days of week and time of day
daysofweek = Group(OneOrMore(Literal("Mo") | Literal("Tu") | Literal("We") | Literal("Th") | Literal("Fr") | Literal("Sa") | Literal("Su") | Literal("Wk") | Literal("Wd") | Literal("Al")))
timeofday = Group(Word(nums,exact=4) + Suppress("-") + Word(nums,exact=4))
tconf_time = negation + daysofweek + timeofday
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

