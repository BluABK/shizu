__author__ = 'BluABK <abk@blucoders.net'

import ConfigParser
import re
from subprocess import check_output


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

cfg = Config()
regex = re.compile(" +")
sambaUsers = list()
loginHandlesRaw = check_output(cfg.rawlogins(), shell=True)
loginHandles = loginHandlesRaw.splitlines()


def getplaying():
    return True


def getlogins():
    return sambaUsers

for index, line in enumerate(loginHandles):
    tmpLine = regex.split(line)
    splitLine = list()
    for test in tmpLine:
        if not ' ' in test:
            splitLine.append(test)
    sambaUsers.insert(index, SambaUser(splitLine[0], splitLine[1], splitLine[3]))


def help():
    cmdlist = list()
    cmdlist.append("Syntax: samba command arg1..argN")
    cmdlist.append("Available commands: logins* (* command contains sub-commands)")
    return cmdlist