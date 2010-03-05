""" timekpr directories """

# TODO: Commented until removed completely
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

# ==============================================================================
# FILES
# Points to file with login defaults
LOGIN_DEFS = '/etc/login.defs'

# Points to log file
LOG_FILE = '/var/log/timekpr.log'

# Points to pam module time.conf and access.conf
PAM_TIME_CONF = '/etc/security/time.conf'
PAM_ACCESS_CONF = '/etc/security/access.conf'

# ==============================================================================
# DIRECTORIES
# Point to directories/folders
SETTINGS_DIR = '/etc/timekpr'
WORK_DIR = '/var/lib/timekpr'
SHARED_DIR = '/usr/share/timekpr'
DAEMON_DIR = '/etc/init.d'



