#!/usr/bin/python
#Prepare gdm and login in /etc/pam.d/

import os.path
import re
import sys

#TODO: os.environ[param] if operating systems have different paths

def pamfilecheck(file):
    """ Checking pam.d files, adds the required lines """
    try:
        f = open(file)
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
        #Didn't find pam_time.so in file - add it
        #write-append
        f = open(file, 'a')
        f.write(str_start + 'account required pam_time.so' + str_end)
        f.close()
    # pam_access
    match_access = re.findall('^account\s+required\s+pam_access.so', contents)
    if not match_access:
        #Didn't find pam_time.so in file - add it
        #write-append
        f = open(file, 'a')
        f.write(str_start + 'account required pam_access.so' + str_end)
        f.close()
    return

def pamconffilecheck(file):
    """ Checks time.conf and access.conf, adds the required TIMEKPR section """
    pass # Disabled
    try:
        f = open(file)
    except IOError, e:
        # Here we fail, we need those two files.
        sys.exit("INFO: " + str(e))
    contents = f.read()
    f.close()

    #time.conf
    match_time = re.findall('^###? TIMEKPR START', contents)
    if match_time:
        #Found timekpr section, uncomment the whole section (commented after removal, see postrm)
        if re.findall('^### TIMEKPR START', contents):
            #newcontents = re.sub('### TIMEKPR START', '', input)
    return

def beginpamcheck():
    file_list = [
        '/etc/pam.d/gdm',
        '/etc/pam.d/kdm',
        '/etc/pam.d/login'
    ]
    for f in file_list:
        pamfilecheck(f)

def beginpamconfcheck():
    file_list = [
        '/etc/security/time.conf',
        '/etc/security/access.conf'
    ]
    for f in file_list:
        pamconffilecheck(f)

def main():
    beginpamcheck()
    beginpamconfcheck()

if __name__ == '__main__':
    main()
