""" Contains timekpr-related directories """

# LOGFILE: Log file
# TIMEKPRDIR: Default directory for per-user configuration and .lock files
# TIMEKPRWORK: Default working directory for .time, .logout, .late files
# TIMEKPRDAEMON: The init script for timekpr daemon

LOGFILE = '/var/log/timekpr.log'
TIMEKPRDIR = '/etc/timekpr'
TIMEKPRWORK = '/var/lib/timekpr'
TIMEKPRSHARED = '/usr/share/timekpr'
TIMEKPRDAEMON = '/etc/init.d/timekpr'
