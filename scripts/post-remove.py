#!/usr/bin/python
# Remove configuration files, comment out the timekpr sections
# Optional argument: purge will completely remove timekpr sections
# Requires: administrative privileges, sed

import os
import os.path
import sys
import shutil

if "purge" in sys.argv:
    PURGE=True
else:
    PURGE=False

#if operating systems have different paths
#PAM_SECURITY_DIR=/etc/security python post-remove.py
try:
    PAM_SECURITY_DIR = os.environ['PAM_SECURITY_DIR']
except KeyError:
    PAM_SECURITY_DIR = "/etc/security"

def folderrm(folder):
    if not os.path.exists(folder):
        return 1
    print "Processing %s" % folder
    try:
        shutil.rmtree(folder)
        print("Removed: " + folder)
    except shutil.Error, e:
        print(str(e))
    except OSError, e:
        print(str(e))

def pamconffilerm(file):
    filewpath = os.path.join(PAM_SECURITY_DIR, file)
    if not os.path.isfile(filewpath):
        return 1
    print "Processing %s" % filewpath
    if PURGE:
        #Comment out the timekpr section
        os.system("sed -i -e '/^### TIMEKPR START/,/^### TIMEKPR END/ s/^#//g' '%s'" % filewpath)
        #Clear it
        os.system("sed -i -e '/^## TIMEKPR START/,/^## TIMEKPR END/d' '%s'" % filewpath)
    else:
        #Just comment it out
        os.system("sed -i -e '/^## TIMEKPR START/,/^## TIMEKPR END/ s/^/#/g' '%s'" % filewpath)

def beginfolderrm():
    if not PURGE: return 1
    folders = [
        '/etc/timekpr',
        '/var/lib/timekpr',
    ]
    for f in folders:
        folderrm(f)

def beginpamconfrm():
    #/etc/security/time.conf
    file_list = [
        'time.conf',
        'access.conf'
    ]
    for f in file_list:
        pamconffilerm(f)

def main():
    beginfolderrm()
    beginpamconfrm()

if __name__ == '__main__':
    main()
