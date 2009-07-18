# Check out: http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION007600000000000000000
from pyparsing import Word, alphas, alphanums, ZeroOrMore, OneOrMore, LineStart, LineEnd, Optional, Group, Combine, Suppress

# define grammar
# services;ttys;users;times
# ! = NOT, & = AND, | = OR
# * = ANY (can be used only once)

tconf_splitchar = Suppress(";")
tconf_commonchars = "*!"
tconf_commonops = "&|"
tconf_services = Group(OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops))))
tconf_ttys = Group(OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops))))
tconf_users = Group(OneOrMore(Word(alphanums + tconf_commonchars) + Optional(Word(tconf_commonops))))
tconf_times = Group(OneOrMore(Word(alphanums + tconf_commonchars + "-") + Optional(Word(tconf_commonops))))
tconf_parser = LineStart() + tconf_services + tconf_splitchar + tconf_ttys + tconf_splitchar + tconf_users + tconf_splitchar + tconf_times + Optional(tconf_splitchar) + LineEnd()


# input string
test = "xsh ; ttyp*;root;!WdMo0000-2400"
moo = "blank & test;tty* & !ttyp*;you|me;!WdMo0000-2400 | !TuFr0800-2400"

# parse input string
print test, "->", tconf_parser.parseString(test)
print moo, "->", tconf_parser.parseString(moo)

