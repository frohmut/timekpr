""" Contains timekpr-related directories """

# LOGFILE: Log file
# TIMEKPRDIR: Default directory for per-user configuration and .lock files
# TIMEKPRWORK: Default working directory for .time, .logout, .late files
# TIMEKPRDAEMON: The init directory for the timekpr init script

# Points to file
LOGFILE = '/var/log/timekpr.log'
# Point to directories
TIMEKPRDIR = '/etc/timekpr'
TIMEKPRWORK = '/var/lib/timekpr'
TIMEKPRSHARED = '/usr/share/timekpr'
TIMEKPRDAEMON = '/etc/init.d'

