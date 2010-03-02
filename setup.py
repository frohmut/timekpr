#!/bin/python
""" timekpr setup.py
    Usage: python setup.py --help

    Requirements:
     - python-distutils
     - python-distutils-extra (https://launchpad.net/python-distutils-extra/+download)
"""

#    Copyright (C) 2009 Savvas Radevic <vicedar@gmail.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#exit("trunk is unstable -- you should not use it to install/test timekpr!")

import sys
import os
import os.path
import glob

from distutils.command.config import config
from distutils.core import setup
#from distutils.core import Command
from DistUtilsExtra.command import *

import timekpr.dirs as dirs
import timekpr.common as common

timekpr_version = common.timekpr_version
VAR = common.timekpr_variables

class config_custom(config):
    # Extend the array of user_options
    config.user_options.extend([
        ('login-defs=', None, 'Path to login defaults file (Default: /etc/login.defs)'),
        ('log-file=', None, 'Path to log file (Default: /var/log/timekpr.log)'),
        ('settings-dir=', None, 'Path to directory for configuration and settings files (Default: /etc/timekpr)'),
        ('work-dir=', None, 'Path to working directory (Default: /var/lib/timekpr)'),
        ('shared-dir=', None, 'Path to shared directory (Default: /usr/share/timekpr)'),
        ('daemon-dir=', None, 'Path to init directory (Default: /etc/init.d)'),
    ])

    def initialize_options(self):
        # Default values
        self.login_defs = "/etc/login.defs"
        self.log_file = '/var/log/timekpr.log'
        self.settings_dir = '/etc/timekpr'
        self.work_dir = '/var/lib/timekpr'
        self.shared_dir = '/usr/share/timekpr'
        self.daemon_dir = '/etc/init.d'
        config.initialize_options(self)

    def finalize_options(self):
        config.finalize_options(self)

    def run(self):
        # Run commands here
        print("test: %s", self.login_defs)
        config.run(self)

#class configure_dirs(Command):
#    description = """ Configure directories in timekpr/dirs.py """
#    user_options = [
#        ('login-defs=', None, 'Path to login.defs file'),
#        ('log-file=', None, 'Path to log file'),
#        ('settings-dir=', None, 'Path to directory for configuration and settings files'),
#        ('work-dir=', None, 'Path to working directory (e.g. for .time, .logout, .late files)'),
#        ('shared-dir=', None, 'Path to shared directory (e.g. for icons and glade files)'),
#        ('daemon-dir=', None, 'Path to init directory (for the timekpr init script)'),
#    ]

#    def initialize_options(self):
#        # Default values
#        self.login_defs = "/etc/login.defs"
#        self.log_file = '/var/log/timekpr.log'
#        self.settings_dir = '/etc/timekpr'
#        self.work_dir = '/var/lib/timekpr'
#        self.shared_dir = '/usr/share/timekpr'
#        self.daemon_dir = '/etc/init.d'
#        pass

#    def finalize_options(self):
#        pass

#    def run(self):
#        print("test: %s", self.login_defs)
#        pass

if sys.version < '2.5':
    sys.exit('ERROR: Sorry, python 2.5 or higher is required for this application.')

setup(
    name = 'timekpr',
    version = timekpr_version,
    url = 'https://launchpad.net/timekpr',

    description = 'Keep control of computer usage',
    long_description = "This program will track and control the computer usage of \
your user accounts. You can limit their daily usage based \
on a timed access duration and configure periods of day \
when they can or cannot log in.",

    author = 'Even Nedberg, Savvas Radevic',
    author_email = 'even@nedberg.net, vicedar@gmail.com',
    maintainer = 'Even Nedberg, Savvas Radevic',
    maintainer_email = 'even@nedberg.net, vicedar@gmail.com',

    license = 'GPL-3',
    keywords = 'system admin time limit access account lock tracking',

    packages = ['timekpr'],
    data_files = [
        ('share/icons/hicolor/scalable/apps', ['artwork/timekpr.svg']),
        ('share/pixmaps', ['data/share/pixmaps/timekpr.xpm']),
        (dirs.TIMEKPR_DAEMON_DIR, ['scripts/timekpr.init'])
    ],
    cmdclass = {
        "build": build_extra.build_extra,
        "build_i18n":  build_i18n.build_i18n,
        "build_help":  build_help.build_help,
        #"build_icons":  build_icons.build_icons,
        "config": config_custom,
        #"configure_dirs": configure_dirs,
    },
    scripts = [
        "scripts/timekpr",
        "scripts/timekprd",
        "scripts/timekpr-gui",
        "scripts/timekpr-client",
    ],
)
