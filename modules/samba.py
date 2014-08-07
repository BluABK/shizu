__author__ = 'BluABK <abk@blucoders.net'

# TODO: Load smbstatus on demand
# TODO: Load smbstatus' BATCHes into separate command
# TODO: Implement user exemption
# TODO: Implement path exemption
# TODO: Add try and SomeReasonableExceptionHandler across code
# TODO: Implement support for checking that samba installation is sane and contains all required binaries and libraries

import ConfigParser
import os
import re
from subprocess import check_output

# Define variables

regex = re.compile(" +")

print check_output("sudo smbstatus -b | grep ipv", shell=True)


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read(os.getcwd() + '/' + "config.ini")

    def loadconfig(self):
        configloc = os.getcwd() + '/' + "config.ini"
        print(configloc)
        self.config.read(configloc)
        return True

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

newlogins = """
def getlogins(msg):
    cfg.loadconfig
    print("Loaded config: " + os.getcwd() + '/' + "config.ini")
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

        loginlist = list()
        matches = re.search(r"samba logins (\w+)", msg)
        try:
            for item in xrange(len(sambausers)):
                if sambausers[item].name == matches.group(1):
                    #if excluded user
                    print "DEBUGZ-A:  %s@%s        [ID: %s]" % (sambausers[item].name, sambausers[item].host, sambausers[item].uid)
                    loginlist.append("%s@%s        [ID: %s]" % (sambausers[item].name, sambausers[item].host, sambausers[item].uid))
        except AttributeError:
                for item in xrange(len(sambausers)):
                    print "DEBUGZ-B:  %s@%s        [ID: %s]" % (sambausers[item].name, sambausers[item].host, sambausers[item].uid)
                    loginlist.append("%s@%s        [ID: %s]" % (sambausers[item].name, sambausers[item].host, sambausers[item].uid))

        for debug in range(len(loginlist)):
            print loginlist[debug]

        return loginlist
"""

def getlogins():
    cfg.loadconfig
    print("Loaded config: " + os.getcwd() + '/' + "config.ini")
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
