#!/usr/bin/python
# Prepare /etc/pam.d/ files and time.conf and access.conf files
# Requires: administrative privileges, sed

import os
import os.path
import re
import sys

#if operating systems have different paths
#PAMD_DIR=/etc/pam.d PAM_SECURITY_DIR=/etc/security post-install.py
try:
    PAMD_DIR = os.environ['PAMD_DIR']
except KeyError:
    PAMD_DIR = "/etc/pam.d"

try:
    PAM_SECURITY_DIR = os.environ['PAM_SECURITY_DIR']
except KeyError:
    PAM_SECURITY_DIR = "/etc/security"

def pamfilecheck(file):
    """ Checking pam.d files, adds the required lines """
    filewpath = os.path.join(PAM_DIR, file)
    try:
        f = open(filewpath)
    except IOError, e:
        print("INFO: " + str(e))
        return 1
    contents = f.read()
    f.close()

    if contents[-1] == '\n':
        str_start = ''
        str_end = '\n'
    else:
        str_start = '\n'
        str_end = ''

    # pam_time
    match_time = re.findall('^account\s+required\s+pam_time.so', contents)
    if not match_time:
        #Didn't find pam_time.so in file - add it (write-append)
        f = open(filewpath, 'a')
        f.write(str_start + 'account required pam_time.so' + str_end)
        f.close()
    # pam_access
    match_access = re.findall('^account\s+required\s+pam_access.so', contents)
    if not match_access:
        #Didn't find pam_time.so in file - add it (write-append)
        f = open(filewpath, 'a')
        f.write(str_start + 'account required pam_access.so' + str_end)
        f.close()
    return

def pamconffilecheck(file):
    """ Checks time.conf and access.conf, adds the required timekpr section """
    filewpath = os.path.join(PAM_SECURITY_DIR, file)
    try:
        f = open(filewpath)
    except IOError, e:
        # Here we fail, we need those two files.
        sys.exit("INFO: " + str(e))
    contents = f.read()
    f.close()

    #time.conf
    match_time = re.findall('^###? TIMEKPR START', contents)
    if match_time:
        #Found timekpr section
        if re.findall('^### TIMEKPR START', contents):
            # Uncomment the whole section (commented after removal, see postrm)
            #FIXME: Use python regex
            p = os.system("sed -i -e '/^### TIMEKPR START/,/^### TIMEKPR END/ s/^#//g' '%s'" % filewpath)
        else:
            #No timekpr section
            p = os.system("sed -i -e '$s/$/\n## TIMEKPR START\n## TIMEKPR END/' '%s'" % filewpath)
    else:
        #Create timekpr section
        p = os.system("sed -i -e '$s/$/\n## TIMEKPR START\n## TIMEKPR END/' '%s'" % filewpath)
    return

def beginpamcheck():
    #/etc/pam.d/gdm
    files = [
        'gdm',
        'kdm',
        'login'
    ]
    for f in files:
        pamfilecheck(f)

def beginpamconfcheck():
    #/etc/security/time.conf
    files = [
        'time.conf',
        'access.conf'
    ]
    for f in files:
        pamconffilecheck(f)

def main():
    beginpamcheck()
    beginpamconfcheck()

if __name__ == '__main__':
    main()
