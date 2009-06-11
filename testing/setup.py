
# Under heavy construction (wear a helmet!)
# http://peak.telecommunity.com/DevCenter/setuptools

# Based on deluge setup.py:
# Copyright (C) 2007 Andrew Resch <andrewresch@gmail.com>

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from setuptools.command.install import install as _install

import msgfmt
import sys
import os
import os.path

timekpr_version = '0.2.2'

if sys.version < '2.5':
    sys.exit('ERROR: Sorry, python 2.5 is required for this application.')

# Variables
try:
    PREFIX = os.environ['PREFIX']
except KeyError:
    PREFIX = "/usr"
try:
    PAMD_DIR = os.environ['PAMD_DIR']
except KeyError:
    PAMD_DIR = "/etc/pam.d"
try:
    PAM_SECURITY_DIR = os.environ['PAM_SECURITY_DIR']
except KeyError:
    PAM_SECURITY_DIR = "/etc/security"

timekpr_data_files = [
    (os.path.join(PREFIX, 'share/icons/hicolor/scalable/apps'),
        ['artwork/timekpr.svg']),
    (os.path.join(PREFIX, 'share/applications'),
        ['data/usr/share/applications/timekpr.desktop']),
    (os.path.join(PREFIX, 'share/pixmaps'),
        ['data/share/pixmaps/timekpr.xpm']),
    ('/etc/init.d/timekpr', ['scripts/timekpr.init']),
]

class build_trans(cmd.Command):
    description = 'Compile .po files into .mo files'

    user_options = [
            ('build-lib', None, "lib build folder")
    ]

    def initialize_options(self):
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_lib'))

    def run(self):
        po_dir = os.path.join(os.path.dirname(__file__), 'i18n/')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:len(f) - 3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join(self.build_lib, 'i18n', lang, \
                        'LC_MESSAGES')
                    dest = os.path.join(dest_path, 'timekpr.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if not os.path.exists(dest):
                        print('Compiling %s' % src)
                        msgfmt.make(src, dest)
                    else:
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime > dest_mtime:
                            print('Compiling %s' % src)
                            msgfmt.make(src, dest)

class install(_install):
    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        _install.run(self)
        if not self.root:
            self.do_egg_install()

class build(_build):
    sub_commands = [('build_trans', None)] + _build.sub_commands
    def run(self):
        # Run all sub-commands (at least those that need to be run)
        _build.run(self)

cmdclass = {
    'build': build,
    'build_trans': build_trans
}

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
    keywords = 'system admin time limit access account',

    entry_points = {
        'console_scripts': ['timekpr = timekpr:main',
        'gui_scripts': ['timekpr-gui = timekpr-gui.main']
    },

    cmdclass = cmdclass,

    packages = ['timekpr'],
    package_data = {
        'timekpr': ['data/etc/*', 'data/share/timekpr/*'],
    },
    include_package_data=True,
    data_files = timekpr_data_files,
    py_modules = ['timekprpam', 'timekprcommon'],
    zip_safe = False,
)
