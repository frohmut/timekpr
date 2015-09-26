#!/usr/bin/python

# Module for timekpr to sync user configuration (and used time)
# across multible machines ('devices').

import requests
from os.path import isfile, getmtime
from socket import gethostname
from pwd import getpwnam,getpwall
from time import strftime
from time import gmtime
from timekprpam import *
from timekprcommon import *
import copy

try:
    # python3
    import configparser
except ImportError:
    # python2.x
    import ConfigParser as configparser

import json

# logging, probably should used logkpr from
# timekpr.py, but wrote this for minimal
# coupling
def log_kpr(var, string,clear = 0):
    try:
        if var['DEBUGME'] != 'True':
                return
        if clear == 1:
                l = open(var['LOGFILE'], 'w')
        else:
                l = open(var['LOGFILE'], 'a')
        nowtime = strftime('%Y-%m-%d %H:%M:%S ')
        l.write(nowtime + string +'\n')
        l.close()
    except:
        # do not stop sync if we cannot write
        # to the log file
        pass

# To use the syncing mechanism the configuration file must contain
# a new section [sync] with the entries 'getjson' and 'postjson'.
# Optionally, an entry 'timeout' can be provided to set the
# timeout for the get/post requests in seconds.
# The values must be full URL to a server that hands out and
# takes a json configuration description.
# Two reference implementations (in node and for fritzbox's ctlmgr
# an be found on github: https://github.com/frohmut/timekpr-server).
def get_server_variables(DEVACTIVE):
    c = dict();

    fconf = '/etc/timekpr.conf'
    if DEVACTIVE:
        fconf = './timekpr.conf'

    if not isfile(fconf):
        exit('Error: Could not find configuration file %s' % fconf)

    try:
        conf = configparser.ConfigParser()
        conf.read(fconf)
        c['getjson'] = conf.get("sync", "getjson")
        c['postjson'] = conf.get("sync", "postjson")
    except (configparser.ParsingError, configparser.NoOptionError, configparser.NoSectionError):
        c['noserver'] = True
    if c.get('getjson') != None:
        try:
            c['timeout'] = float(conf.get("sync", "timeout"))
        except configparser.NoOptionError:
            c['timeout'] = 3.0
    return c

# get configuration (as json) from a server
def get_json(url, timeout):
    try:
        r = requests.get(url, timeout=timeout)
        return r.json()
    except requests.exceptions.Timeout:
        return { "error": "server timeout" }

# post the modified configuration to a server (as json)
def post_json(url, data, timeout):
    try:
        json_text = json.dumps(data)
        d = {}
        d['json'] = json_text + "\n"
        r = requests.post(url, data=d, timeout=timeout)
        if r != json_text:
            return False
        else:
            return True
    except requests.exceptions.Timeout:
        return False

# get all local accounts
def get_local_accounts():
    return dict((acc[0], True) for acc in getpwall())

# take the time from the local time file of the user
def get_time(tfile, username):
    if isfile(tfile) and fromtoday(tfile):
        t = open(tfile)
        time = int(t.readline())
        t.close()
        return time
    else:
        return 0

# write the timee to the local time file of the user
def write_time(var, user, time):
    timefile = var['TIMEKPRWORK'] + '/' + user + '.time'
    f = open(timefile, 'w')
    f.write(str(time))
    f.close()


# get the current local information for a user
def get_local_config_for_user(var, user):
    conffile = var['TIMEKPRDIR'] + '/' + user
    timefile = var['TIMEKPRWORK'] + '/' + user + '.time'
    limits, x, y = readusersettings(user, conffile)
    islocked = isuserlocked(user)
    time = get_time(timefile, user)
    return islocked, time, limits

# write the limits file
#
# For the sync mechanism, currently only one daily limit
# is supported. This limit is used 7 times for the local
# limit file.
def write_limits(var, user, daily_limit):
    conffile = var['TIMEKPRDIR'] + '/' + user
    f = open(conffile, 'w')
    f.write("limit=( " + (str(daily_limit) + " ") * 7 + ")")
    f.close()


# update the server_config dictionary
# requires: no changes were made on the server side
# if changes were mode on the server side, must be
# called before the call to read_from_local
def read_from_local(var, server_conf):
    log_kpr(var, "read from local")
    # for every user under timekpr control
    #   set local data in server_conf object
    ls = parseutlist(parsetimeconf())
    for user, [bfrom, bto] in ls:
        islocked, time, limits = get_local_config_for_user(var, user)
        # if neccessary, add local users
        if not server_conf['users'].get(user):
            server_conf['users'][user] = {}
        # set the server config from local information
        server_conf['users'][user]['userlocked'] = islocked
        server_conf['users'][user]['limit'] = limits[0]
        server_conf['users'][user]['time'] = time

# update local file from server configuration
# return False, if nothing was changed (or couldn't be changed)
# and True otherwise
def update_from_server(server_conf, hostname, var):
    if server_conf.get('users') == None:
        log_kpr(var, "no users in the server config")
        return False
    if server_conf.get('devices') == None:
        log_kpr(var, "devices not found")
        return False
    if server_conf['devices'].get(hostname) == None:
        log_kpr(var, "own host not found")
        return False
    if server_conf['devices'][hostname].get("checked_change") == None:
        log_kpr(var, "own host without timestamp")
        return False
    if server_conf.get("last_change") == None:
        log_kpr(var, "server without timestamp")
        return False

    if server_conf['devices'][hostname]['checked_change'] == server_conf["last_change"]:
        return False

    log_kpr(var, "update from server")
    accounts = get_local_accounts()
    for user in server_conf['users']:
        # Check if the user on the server also exists as account
        # on the local device/machine.
        # We don't need to care if is a 'normal' user or not.
        if accounts.get(user) != None:
            u = server_conf['users'][user]
            islocked, time, limits = get_local_config_for_user(var, user)
            if u['userlocked'] != islocked:
                if u['userlocked'] == True:
                    lockuser(user)
                else:
                    unlockuser(user)

            if u['limit'] != limits[0]:
                write_limits(var, user, u['limit'])

            # The whole bonus/penalty feature in in timekpr is
            # hacked in (just changes the used time per user)
            # To sidestep the real issue, we write the
            # used time of a user from the server,
            # if
            # - the used time is bigger than the local used time
            # - or is more than 3 minutes smaller.
            if u['time'] > time or ((time - u['time'])/60.0) > 3:
                    write_time(var, user, u['time'])

    return True

def do_sync_server_config():
    server_var = get_server_variables(False)
    # if no server is used: return
    if server_var.get('noserver') == True:
        return

    var = getvariables(False)
    server_conf = get_json(server_var['getjson'], server_var['timeout'])
    # server error?
    if server_conf.get("error") != None:
        log_kpr(var, "server error: " + server_conf.get("error"))
        return

    # make a copy to check for changes
    # easier than to keep track of changes to
    # the configuration manually
    orig_server_conf = copy.deepcopy(server_conf)

    hostname = gethostname()

    # bootstrapping: if this is the first sync run on the
    # whole home network, the server configuration may be
    # empty, so start to fill it
    if server_conf.get('users') == None:
        server_conf['users'] = {}
    if server_conf.get('devices') == None:
        server_conf['devices'] = {}
    if server_conf.get('last_change') == None:
        server_conf['last_change'] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    # if this was the first run with this device/machine, add the
    # device information
    if server_conf['devices'].get(hostname) == None:
        server_conf['devices'][hostname] = {}
        server_conf['devices'][hostname]['checked_change'] = 0


    updated_from_server = update_from_server(server_conf, hostname, var)

    read_from_local(var, server_conf)

    # if we changed the server config from the local files
    # modify the last_change flag
    if orig_server_conf != server_conf:
        server_conf['last_change'] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    # if we updated to the latest server version or
    # modified the server config, send an update to the server
    if updated_from_server or orig_server_conf != server_conf:
        server_conf['devices'][hostname]['checked_change'] = server_conf['last_change']
        log_kpr(var, "posting modified configuration")
        ok = post_json(server_var['postjson'], server_conf, server_var['timeout'])
        if not ok:
            log_kpr(var, "server sync failed")

def syncserverconfig():
    try:
        do_sync_server_config()
    except Exception as e:
        # the server extension should be completely optional
        # if something doesn't work (server is down, etc.)
        # just ignore it
        # "print": Not sure what to do here. Try to read
        # the logging-var from the config file? Way too
        # much work ;-)
        print "error: " + str(e)


if __name__ == "__main__":

    syncserverconfig()


