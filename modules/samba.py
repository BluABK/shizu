__author__ = 'BluABK <abk@blucoders.net'

# TODO: Load smbstatus' BATCHes into separate command
# TODO: Implement user exemption
# TODO: Implement path exemption
# TODO: Add try and SomeReasonableExceptionHandler across code
# TODO: Implement support for checking that samba installation is sane and contains all required binaries and libraries
# TODO: Implement nowplaying() that fetches BATCH media files from smbstatus for SambaUsers, ex: !np Heretic121
import ConfigParser
import os
import re
#from sys import exc_info
from subprocess import check_output
import os
import colours as clr

# Define variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.green
commandsavail = "logins np"

regex = re.compile(" +")


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
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
    pid = 0
    host = ''
    playing = ''

    def __init__(self, uid, name, host):
        self.name = name
        self.pid = uid
        self.host = host

        def setplaying(media):
            self.playing = media

        def nowplaying():
            return self.playing


def getplaying():
    tmp = check_output("sudo smbstatus -vvv | grep BATCH | grep DENY_WRITE | grep -v \.jpg | grep -v \.png", shell=True)
    handles = tmp.splitlines()
    playing = list()

    for index, line in enumerate(handles):
        # throw out empty lines
        if not len(line):
            continue

        tmpline = regex.split(line)
        splitline = list()

        for test in tmpline:
            if not ' \t' in test:
                print test
                splitline.append(test)

        if len(splitline) < 4:
            # TODO investigate
            print "splitline had wrong length: %s" % str(len(splitline))
        else:
            playing.insert(index, SambaUser(splitline[0], splitline[1], splitline[3]))

    return playing


def getlogins(msg):
    global cfg
    #TODO: cfg.loadconfig seems to have no effect according to PyCharm o0
    cfg.loadconfig
    loginhandlesraw = check_output(cfg.rawlogins(), shell=True)
    loginhandles = loginhandlesraw.splitlines()
    sambausers = list()

    for index, line in enumerate(loginhandles):
        # throw out empty lines
        if not len(line):
            continue

        tmpline = regex.split(line)
        splitline = list()

        for test in tmpline:
            if not ' ' in test:
                splitline.append(test)

        if len(splitline) < 4:
            # TODO investigate
            print "samba/getlogins: splitline has not enough items, are you root?"
        else:
            sambausers.insert(index, SambaUser(splitline[0], splitline[1], splitline[3]))

    loginlist = list()

    longestname = 0
    try:
        for item in xrange(len(sambausers)):
            if not len(msg) or sambausers[item].name in msg:
                if len(sambausers[item].name) > longestname:
                    longestname = len(sambausers[item].name)
        loginlist.append("[ID]        user@host")
        for item in xrange(len(sambausers)):
            if not len(msg) or sambausers[item].name in msg:
                #if excluded user
                loginlist.append("[ID: %s] %s@%s" % (sambausers[item].pid.zfill(5), sambausers[item].name,
                                                     sambausers[item].host))
    except:
        loginlist.append("Ouch, some sort of unexpected exception occurred, have fun devs!")
#        loginlist.append("Exception:")
#        for err in xrange(len(exc_info())):
#            loginlist.append(exc_info()[err])
#        raise
    return loginlist


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %ssamba command arg1..argN" % cmdsym)
    cmdlist.append("Available commands: logins* (* command contains sub-commands)")
    return cmdlist
