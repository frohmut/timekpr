
# Under heavy construction (wear a helmet!)
# http://peak.telecommunity.com/DevCenter/setuptools

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import sys
import os

timekpr_version = '0.2.2'

if sys.version < '2.5':
    sys.exit('ERROR: Sorry, python 2.5 is required for this application.')

# Main setup
PREFIX = "/usr/"

timekpr_data_files = [
    (os.path.join(PREFIX, 'share/icons/hicolor/scalable/apps'),
        ['artwork/timekpr.svg']),
    (os.path.join(PREFIX, 'share/applications'),
        ['data/share/applications/timekpr.desktop']),
    (os.path.join(PREFIX, 'share/pixmaps'),
        ['data/share/pixmaps/timekpr.png']),
    ('/etc/init.d/timekpr', ['scripts/timekpr.init']),
]

setup(
    name = 'timekpr',
    version = timekpr_version,
    url = 'http://launchpad.net/timekpr',

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
    keywords = 'system admin time limit access account',

    entry_points = {
        'console_scripts': [
            'timekprd = timekprd.todo:todo_func',
            'timekpr-gui = timekpr-gui.todo2:todo2_func',
        ]
    },

    packages = ['timekprd', 'timekpr-gui', 'timekpr-client'],
    package_data = {'timekprd': ['data/etc/*'],
                    'timekpr-gui': ['data/share/timekpr/*'],
                    'timekpr-client': [],
                    }
    data_files=timekpr_data_files,
    py_modules=['timekprpam.timekprpam', 'timekprcommon.timekprcommon'],
    zip_safe=False,
)
