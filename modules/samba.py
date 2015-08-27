#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess

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


class FileLock:
    def __init__(self):
        self.dump = check_output("sudo smbstatus -L -d 11")
        self.locks = self.dump.split("parse_share_modes:")

    def get_amount(self):
        return len(self.locks)


def format_mediainfo(playback, criteria, args, format_list):
    shellex = check_output("mediainfo \"%s\" | grep \"%s\" | %s" % (playback.get_path(), criteria, args),
                           shell=True).strip('\n')
    if shellex is not None:
        print shellex
        li = re.split(r'\s{2,}: ', shellex.strip('\n'))
        if criteria in li:
            format_list[criteria] = li[li.index(criteria) + 1]
            print format_list
            return format_list
        else:
            return format_list
    else:
        return None


def format_np(format_dict):
    output = ""

    if "Album/Performer" in format_dict:
        output += "%s ft " % format_dict["Album/Performer"]
    if "Performer" in format_dict:
        output += "%s" % format_dict["Performer"]
    else:
        output += "No Artist"
    if "Album" in format_dict:
        output += "- %s" % format_dict["Album"]
    if "ISBN" in format_dict:
        output += " [%s]" % format_dict["ISBN"]
    if "Track name" in format_dict:
        output += " - %s" % format_dict["Track name"]
    # Format metadata
    output += " <"
    if "Bit rate" in format_dict:
        output += "%s" % format_dict["Bit rate"]
    if "Format" in format_dict:
        output += " %s" % format_dict["Format"]
    if "Bit depth" in format_dict:
        output += " %s" % format_dict["Bit depth"]
    output += ">"
    print output

    return output


def get_playing2():
    locks__num = FileLock.get_amount()
    return str(locks__num)


def get_playing():
    tmp = check_output("sudo smbstatus -L -vvv | grep BATCH | grep DENY_WRITE | grep -v \.jpg | grep -v \.png",
                       shell=True)
    print tmp
    handles = tmp.splitlines()

    li = list()
    for index, line in enumerate(handles):
        # throw out empty lines
        if not len(line):
            continue
        tmp_line = re.split(r'\s{2,}', line)
        print tmp_line
        date = tmp_line[-1]

        path = tmp_line[-3] + "/" + tmp_line[-2]

        new_playback = Playback(path)
        new_playback.set_stringdate(date)
        li.append(new_playback)

    tmp_playback = Playback()
    for playback in li:
        if playback.get_date() > tmp_playback.get_date():
            tmp_playback = playback
    #try:
    print tmp_playback.get_path()
    format_dict= {}
    format_dict = format_mediainfo(tmp_playback, "Performer", "tail -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Track name", "head -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Album", "grep -v \"Album/Performer\" | tail -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Album/Performer", "tail -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "ISBN", "grep -v \"Comment\" | tail -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Format", "head -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Bit depth", "head -n1", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Bit rate", "tail -n1", format_dict)

    return format_np(format_dict)
    #except:
    return "Shell execute failed =/"


def get_logins(msg):
    global cfg
    # TODO: cfg.loadconfig seems to have no effect according to PyCharm o0
    cfg.loadconfig
    login_handles_raw = check_output(cfg.rawlogins(), shell=True)
    login_handles = login_handles_raw.splitlines()
    samba_users = list()

    for index, line in enumerate(login_handles):
        # throw out empty lines
        if not len(line):
            continue

        tmp_line = regex.split(line)
        split_line = list()

        for test in tmp_line:
            if not ' ' in test:
                split_line.append(test)

        if len(split_line) < 4:
            # TODO investigate
            print "samba/getlogins: split_line has not enough items, are you root?"
        else:
            samba_users.insert(index, SambaUser(split_line[0], split_line[1], split_line[3]))

    login_list = list()

    longestname = 0
    try:
        for item in xrange(len(samba_users)):
            if not len(msg) or samba_users[item].name in msg:
                if len(samba_users[item].name) > longestname:
                    longestname = len(samba_users[item].name)
        login_list.append("[ID]        user@host")
        for item in xrange(len(samba_users)):
            if not len(msg) or samba_users[item].name in msg:
                # if excluded user
                login_list.append("[ID: %s] %s@%s" % (samba_users[item].pid.zfill(5), samba_users[item].name,
                                                      samba_users[item].host))
    except:
        login_list.append("Ouch, some sort of unexpected exception occurred, have fun devs!")
    # login_list.append("Exception:")
    #        for err in xrange(len(exc_info())):
    #            login_list.append(exc_info()[err])
    #        raise
    return login_list


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %ssamba command arg1..argN" % cmdsym)
    cmdlist.append("Available commands: logins* (* command contains sub-commands)")
    return cmdlist
