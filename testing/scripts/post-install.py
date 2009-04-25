#!/usr/bin/python
#Prepare gdm and login in /etc/pam.d/

import os.path
import re

def pamgdm(file='/etc/pam.d/gdm'):
    if not os.path.isfile(file):
        return
    f = open(file)
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

def pamkdm(file='/etc/pam.d/kdm'):
    return

def pamlogin(file='/etc/pam.d/login'):
    return


if __name__ == '__main__':
    pamgdm()
