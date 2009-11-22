""" Contains timekpr-related directories.
    Packagers should patch this module, or we ought to use some sort of 
    installation method:
    a) scons? Note: Check gpick project
    b) normal simple config?
"""

# LOGFILE: Log file
# TIMEKPRDIR: Default directory for per-user configuration and .lock files
# TIMEKPRWORK: Default working directory for .time, .logout, .late files
# TIMEKPRDAEMON: The init directory for the timekpr init script

## Points to file
#LOGFILE = '/var/log/timekpr.log'
## Point to directories
#TIMEKPRDIR = '/etc/timekpr'
#TIMEKPRWORK = '/var/lib/timekpr'
#TIMEKPRSHARED = '/usr/share/timekpr'
#TIMEKPRDAEMON = '/etc/init.d'

# Points to file
LOG_FILE = '/var/log/timekpr.log'
# Point to directories
TIMEKPR_SETTINGS_DIR = '/etc/timekpr'
TIMEKPR_WORK_DIR = '/var/lib/timekpr'
TIMEKPR_SHARED_DIR = '/usr/share/timekpr'
TIMEKPR_DAEMON_DIR = '/etc/init.d'
