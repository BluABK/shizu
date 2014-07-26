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

def getPlaying():
    return True

def getLogins():
    return sambaUsers

#    tmpLogins = list()
#
#    for index,user in enumerate(sambaUsers.):
#        tmpLogins.insert(index, user[0], user[1], user[3])
#
 #       return tmpLogins

class sambaUser:
    name = ''
    id = 0
    host = ''
    playing = ''

    def __init__(self, id, name, host):
        self.name = name
        self.id = id
        self.host = host

        def setPlaying(media):
            self.playing = media

        def nowPlaying():
            return self.playing

for index, line in enumerate(loginHandles):
 #   print('DEBUG: index ' + str(index) + ':    ' + line)
    tmpLine = regex.split(line)

    splitLine = list()
    for metaIndex, test in enumerate(tmpLine):
        if not test.__contains__(' '):
            splitLine.append(test)

    sambaUsers.insert(index, sambaUser(splitLine[0], splitLine[1], splitLine[3]))
 #   print('DEBUG: Creating user ' + splitLine[0] + ' ' + splitLine[1] + ' ' + splitLine[3])
    print('Successfully created user #' + str(index) + ': ' + str(sambaUsers[index].id) + ' - ' + sambaUsers[index].name + '@' + sambaUsers[index].host + '.')
