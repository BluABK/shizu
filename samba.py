__author__ = 'BluABK <abk@blucoders.net'

# TODO: Load smbstatus on demand
# TODO: Load smbstatus' BATCHes into separate command
# TODO: Implement user exemption
# TODO: Implement path exemption
# TODO: Implement samba directory and file index (probably via server-side mlocate db)
# TODO: Implement search/lookup for aforementioned index
# TODO: Implement "new files" func (13:37 shizu > New file: tv-series/TUTVS/The.Ultimate.TV-Series.4K.FLAC-iNSANE.mkv)
# TODO: Add try and SomeReasonableExceptionHandler across code
# TODO: Implement support for checking that samba installation is sane and contains all required binaries and libraries

import ConfigParser
import re
from subprocess import check_output

# Define variables
global re
global cfg

regex = re.compile(" +")


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read("config.ini")

    def rawlogins(self):
        return str(self.config.get('samba', 'smbstatus-command'))

    def excludelogins(self):
        return str(self.config.get('samba', 'exclude-names'))

    def excludepaths(self):
        return str(self.config.get('samba', 'exclude-paths'))

cfg = Config()


class SambaUser:
    name = ''
    uid = 0
    host = ''
    playing = ''

    def __init__(self, uid, name, host):
        self.name = name
        self.uid = uid
        self.host = host

        def setplaying(media):
            self.playing = media

        def nowplaying():
            return self.playing


def getplaying():
    return True


def getlogins():
    loginhandlesraw = check_output(cfg.rawlogins(), shell=True)
    loginhandles = loginhandlesraw.splitlines()
    sambausers = list()

    for index, line in enumerate(loginhandles):
        tmpline = regex.split(line)
        splitline = list()
        for test in tmpline:
            if not ' ' in test:
                splitline.append(test)
        sambausers.insert(index, SambaUser(splitline[0], splitline[1], splitline[3]))

    return sambausers


def help():
    cmdlist = list()
    cmdlist.append("Syntax: samba command arg1..argN")
    cmdlist.append("Available commands: logins* (* command contains sub-commands)")
    return cmdlist