__author__ = 'bluabk'

from subprocess import check_output
import re
import config

regex = re.compile(" +")
sambaUsers = list()

#print 'test'
#call(['echo', 'shellexectest'])

loginHandlesRaw = check_output(config.config.get('samba', 'smbstatus-command'), shell=True)

print loginHandlesRaw

loginHandles = loginHandlesRaw.splitlines()


def getplaying():
    return True


def getlogins():
    return sambaUsers


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
    cmdlist.append("Available commands: logins (* command contains sub-commands)")
    return cmdlist