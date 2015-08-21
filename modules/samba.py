#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# from sys import exc_info
from subprocess import check_output
import os
import datetime
import time
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


class Playback:
    def __init__(self, path="", date=time.gmtime(0)):
        self.path = path
        self.date = date

    def set_path(self, new_path):
        self.path = new_path

    def get_path(self):
        return self.path

    def set_date(self, new_date):
        self.date = new_date

    def get_date(self):
        return self.date

    def set_stringdate(self, new_date):
        self.date = time.strptime(str(new_date), '%a %b %d %H:%M:%S %Y')


def get_playing():
    tmp = check_output("sudo smbstatus -L -vvv | grep BATCH | grep DENY_WRITE | grep -v \.jpg | grep -v \.png",
                       shell=True)
    handles = tmp.splitlines()

    li = list()
    for index, line in enumerate(handles):
        # throw out empty lines
        if not len(line):
            continue

        tmp_line = re.split(r'\s{2,}', line)

        date = tmp_line[-1]
        path = tmp_line[-3] + "/" + tmp_line[-2]

        new_playback = Playback(path)
        new_playback.set_stringdate(date)
        li.append(new_playback)

    tmp_playback = Playback()
    for playback in li:
        if playback.get_date() > tmp_playback.get_date():
            tmp_playback = playback

    artist = re.split(r'\s{2,}: ',
                      check_output("mediainfo \"%s\" | grep Performer | tail -n1" % tmp_playback.get_path(),
                                   shell=True))[-1].strip('\n')
    title = re.split(r'\s{2,}: ',
                     check_output("mediainfo \"%s\" | grep \"Track name\" | head -n1" % tmp_playback.get_path(),
                                  shell=True))[-1]
    album = re.split(r'\s{2,}: ',
                      check_output("mediainfo \"%s\" | grep Album | tail -n1" % tmp_playback.get_path(),
                                   shell=True))[-1]
    codec = re.split(r'\s{2,}: ',
                      check_output("mediainfo \"%s\" | grep Format | head -n1" % tmp_playback.get_path(),
                                   shell=True))[-1]
    bitdepth = re.split(r'\s{2,}: ',
                      check_output("mediainfo \"%s\" | grep \"Bit depth\" | head -n1" % tmp_playback.get_path(),
                                   shell=True))[-1]
    bitrate = re.split(r'\s{2,}: ',
                      check_output("mediainfo \"%s\" | grep \"Bit rate\" | tail -n1" % tmp_playback.get_path(),
                                   shell=True))[-1]
    print artist
    print title
    print album
    print codec
    print bitrate
    print bitdepth
    sep = " - "
    fancy_start = "["  # u'\u300E'  # u"\u300E"  # "『"
    fancy_end = "]"  # u'\u300F'  # "』"
    np_format = str(artist + sep + album + sep + title + "[" + bitrate + " " + codec + " (" + bitdepth + ")" "]")
    return np_format


def getlogins(msg):
    global cfg
    # TODO: cfg.loadconfig seems to have no effect according to PyCharm o0
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
                # if excluded user
                loginlist.append("[ID: %s] %s@%s" % (sambausers[item].pid.zfill(5), sambausers[item].name,
                                                     sambausers[item].host))
    except:
        loginlist.append("Ouch, some sort of unexpected exception occurred, have fun devs!")
    # loginlist.append("Exception:")
    #        for err in xrange(len(exc_info())):
    #            loginlist.append(exc_info()[err])
    #        raise
    return loginlist


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %ssamba command arg1..argN" % cmdsym)
    cmdlist.append("Available commands: logins* (* command contains sub-commands)")
    return cmdlist
