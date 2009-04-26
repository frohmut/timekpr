#!/usr/bin/python
# Prepare /etc/pam.d/ files and time.conf and access.conf files
# Needs administrative privileges

import os
import os.path
import re
import sys

#if operating systems have different paths
#PAMD_DIR=/etc/pam.d PAM_SECURITY_DIR=/etc/security post-install.py
try:
    PAMD_DIR = os.environ['PAMD_DIR'].rstrip('/')
except KeyError:
    PAMD_DIR = "/etc/pam.d"

try:
    PAM_SECURITY_DIR = os.environ['PAM_SECURITY_DIR'].rstrip('/')
except KeyError:
    PAM_SECURITY_DIR = "/etc/security"

def pamfilecheck(file):
    """ Checking pam.d files, adds the required lines """
    try:
        f = open(PAM_DIR + '/' + file)
    except IOError, e:
        print("INFO: " + str(e))
        return
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
        f = open(file, 'a')
        f.write(str_start + 'account required pam_time.so' + str_end)
        f.close()
    # pam_access
    match_access = re.findall('^account\s+required\s+pam_access.so', contents)
    if not match_access:
        #Didn't find pam_time.so in file - add it (write-append)
        f = open(PAM_DIR + '/' + file, 'a')
        f.write(str_start + 'account required pam_access.so' + str_end)
        f.close()
    return

def pamconffilecheck(file):
    """ Checks time.conf and access.conf, adds the required timekpr section """
    pass # Disabled
    try:
        f = open(PAM_SECURITY_DIR + '/' + file)
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
            p = os.system("sed -i -e '/^### TIMEKPR START/,/^### TIMEKPR END/ s/^#//g' %s" % file)
        else:
            #No timekpr section
            p = os.system("sed -i -e '$s/$/\n## TIMEKPR START\n## TIMEKPR END/' %s" % file)
    else:
        #Create timekpr section
        p = os.system("sed -i -e '$s/$/\n## TIMEKPR START\n## TIMEKPR END/' %s" % file)
    return

def beginpamcheck():
    #/etc/pam.d/gdm
    file_list = [
        'gdm',
        'kdm',
        'login'
    ]
    for f in file_list:
        pamfilecheck(f)

def beginpamconfcheck():
    #/etc/security/time.conf
    file_list = [
        'time.conf',
        'access.conf'
    ]
    for f in file_list:
        pamconffilecheck(f)

def main():
    beginpamcheck()
    beginpamconfcheck()

if __name__ == '__main__':
    main()
