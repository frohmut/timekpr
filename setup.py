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

exit("trunk is unstable -- you should not use it to install/test timekpr!")

import sys
import os
import os.path
import glob

from distutils.core import setup
from DistUtilsExtra.command import *

import timekpr.dirs as dirs
import timekpr.common as common

timekpr_version = common.timekpr_version
VAR = common.timekpr_variables

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
    },
    scripts = [
        "scripts/timekpr",
        "scripts/timekprd",
        "scripts/timekpr-gui",
        "scripts/timekpr-client",
    ],
)
