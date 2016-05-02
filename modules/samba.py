#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import re
# from sys import exc_info
from subprocess import check_output, CalledProcessError
import os
import time
import json
import colours as clr

__author__ = 'BluABK <abk@blucoders.net'

# TODO: Load smbstatus' BATCHes into separate command
# TODO: Implement user exemption
# TODO: Implement path exemption
# TODO: Add try and SomeReasonableExceptionHandler across code
# TODO: Implement support for checking that samba installation is sane and contains all required binaries and libraries
# TODO: Implement now playing() that fetches BATCH media files from smbstatus for SambaUsers, ex: !np Heretic121


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
        try:
            self.date = time.strptime(str(new_date), '%a %b %d %H:%M:%S %Y')
        except ValueError:
            self.date = "ValueError"
            return False
        return True


class FileLock:
    def __init__(self):
        self.dump = check_output("sudo smbstatus -L -d 11", shell=True)
        # self.locks = self.dump.split(r'parse_share_modes:')
        self.locks = self.dump.splitlines()

    def get_amount(self):
        return len(self.locks)

    def get_lock(self, id):
        return self.locks[id]


def format_mediainfo(playback, criteria, args, format_list):
    shellex = check_output("mediainfo \"%s\" | grep \"%s\" | %s" % (playback.get_path(), criteria, args),
                           shell=True).strip('\n')
    if shellex is not None:
        print "mediainfo dump:"
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


def format_exiftool(playback, criteria, format_list):
    shellex = check_output("exiftool -json \"%s\"" % (playback.get_path()), shell=True)
    if shellex is not None:
        print "exiftool dump:"
        print shellex
        dic = json.loads(shellex)[0]
        if criteria in dic:
            format_list[criteria] = dic.get(criteria)
            return format_list
        else:
            return format_list
    else:
        return None


def format_np(format_dict):
    output = ""

    if "Albumartist" in format_dict:
        if "Artist" in format_dict and format_dict["Albumartist"] != format_dict["Artist"]:
            output += "%s ft " % format_dict["Albumartist"]
    if "Artist" in format_dict:
        output += "%s" % format_dict["Artist"]
    else:
        output += "No Artist"
    if "Album" in format_dict:
        output += " - %s" % format_dict["Album"]
    else:
        output += " - No Album"
    if "Isbn" in format_dict:
        output += " [%s]" % format_dict["Isbn"]
    if "Title" in format_dict:
        output += " - %s" % format_dict["Title"]
    # Format metadata, ignore in case of No artist *and* no album
    if "Artist" in format_dict or "Albumartist" in format_dict or "Album" in format_dict:
        output += " <"
        # TODO: Depends on mediainfo
        if "Bit rate" in format_dict:
            output += "%s" % format_dict["Bit rate"]
        if "FileType" in format_dict:
            output += " %s" % format_dict["FileType"]
        if "BitsPerSample" in format_dict:
            output += " %s-bit" % format_dict["BitsPerSample"]
        output += ">"
    print output

    return output


def format_np_mediainfo(format_dict):
    output = ""

    if "Album/Performer" in format_dict:
        if "Performer" in format_dict and format_dict["Album/Performer"] != format_dict["Performer"]:
            output += "%s ft " % format_dict["Album/Performer"]
    if "Performer" in format_dict:
        output += "%s" % format_dict["Performer"]
    else:
        output += "No Artist"
    if "Album" in format_dict:
        output += " - %s" % format_dict["Album"]
    else:
        output += " - No Album"
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
    locks = FileLock()
    print "==============="
    for i in xrange(locks.get_amount()):
        print locks.get_lock(i)
    print "==============="
    locks__num = locks.get_amount()
    return str(locks__num)


def get_playing():
    try:
        status = check_output("sudo smbstatus -L -vvv | grep BATCH | grep DENY_WRITE | grep -v \.jpg | grep -v \.png",
                           shell=True)
    except CalledProcessError as cpe:
        # Sometimes BATCH mode isn't set, most cases seem to be ressume playback after the handle is gone
        print "smbstatus: grep BATCH failed, trying without."
        status = check_output("sudo smbstatus -L -vvv | grep DENY_WRITE | grep -v \.jpg | grep -v \.png",
                           shell=True)
    except Exception as e:
        raise e
    print status
    handles = status.splitlines()

    li = list()
    for index, line in enumerate(handles):
        # throw out empty lines
        if not len(line):
            continue

        # This is required for later versions, because it makes nonsensical spacing
        samba_raw = line.split()
        print "raw: %s" % samba_raw
        mount_found = False
        date = ' '.join(samba_raw[-5:])
        samba_meta = []
        path = []
        for item in samba_raw[:-5]:
            if '/' in item:
                # Signal that the path has begun and add a missing trailing / to mount point item
                mount_found = True
                item += '/'
            if mount_found:
                path.append(item)
            else:
                samba_meta.append(item)

        # Join mountpoint to path
        path = path[0] + ' '.join(path[1:])
        """
        tmp = ""
        for item in path:
            if item is not path[-1]:
                tmp += item + ' '
            else:
                tmp += item
        path = tmp
        """
        print "meta: %s\npath: %s\ndate: %s" % (samba_meta, path, date)

        test_playback = Playback("test")

        """ [Deprecated in later versions of samba]

        # This is sufficient for older samba
        # tmp_line = re.split(r'\s{3,}', line)

        if test_playback.set_stringdate(tmp_line[-1]):
            print "Two-numeric date"
            date = tmp_line[-1]
            path = tmp_line[5] + "/"
            # Merge multiple path items to one
            for path_item in tmp_line[6:-1]:
                path += path_item
        else:
            print "One-numeric date"
            # In case of one-numeric day, add next last item to last
            date = (tmp_line[-2] + "  " + tmp_line[-1])
            path = tmp_line[5] + "/"
            # Merge multiple path items to one
            for path_item in tmp_line[6:-2]:
                path += path_item
        """
        new_playback = Playback(path)
        new_playback.set_stringdate(date)
        li.append(new_playback)

    tmp_playback = Playback()
    for playback in li:
        if playback.get_date() > tmp_playback.get_date():
            tmp_playback = playback
    # try:
    print tmp_playback.get_path()
    format_dict = {}
    # format_dict = format_mediainfo(tmp_playback, "Performer", "tail -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "Track name", "head -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "Album", "grep -v \"Album/Performer\" | tail -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "Album/Performer", "tail -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "ISBN", "grep -v \"Comment\" | tail -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "Format", "head -n1", format_dict)
    # format_dict = format_mediainfo(tmp_playback, "Bit depth", "head -n1", format_dict)
    format_dict = format_exiftool(tmp_playback, "Artist", format_dict)
    format_dict = format_exiftool(tmp_playback, "Title", format_dict)
    format_dict = format_exiftool(tmp_playback, "Album", format_dict)
    format_dict = format_exiftool(tmp_playback, "Albumartist", format_dict)
    format_dict = format_exiftool(tmp_playback, "Isbn", format_dict)
    format_dict = format_exiftool(tmp_playback, "FileType", format_dict)
    format_dict = format_exiftool(tmp_playback, "BitsPerSample", format_dict)
    format_dict = format_mediainfo(tmp_playback, "Bit rate", "tail -n1", format_dict)

    return format_np(format_dict).encode('utf-8')
    # except:
    # return "Shell execute failed =/"


def get_logins(msg):
    global cfg
    # TODO: cfg.loadconfig seems to have no effect according to PyCharm o0
    # cfg.loadconfig
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
            if ' ' not in test:
                split_line.append(test)

        if len(split_line) < 4:
            # TODO investigate
            print "samba/getlogins: split_line has not enough items, are you root?"
        else:
            samba_users.insert(index, SambaUser(split_line[0], split_line[1], split_line[3]))

    login_list = list()

    longest_name = 0
    try:
        for item in xrange(len(samba_users)):
            if not len(msg) or samba_users[item].name in msg:
                if len(samba_users[item].name) > longest_name:
                    longest_name = len(samba_users[item].name)
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

def help(nick, chan):
    return {
        "samba logins": "<user>",
        "samba np": "",
        "samba np2": "",
        "samba debug": ""
    }

def commands():
    return { "samba": command_samba }

def command_samba(nick, chan, cmd, irc):
    if len(cmd) >= 1:
        cmd[0] = cmd[0].lower()
        if cmd[0] == "logins":
            irc.sendmsg(get_logins(cmd[1:]), chan)
        elif cmd[0] == "np":
            irc.sendmsg(get_playing(), chan)
        elif cmd[0] == "np2":
            irc.sendmsg(get_playing2(), chan)
        elif cmd[0] == "debug":
            dbg = get_logins(cmd[1:])
            irc.debug("Passed variable of length:" + str(len(dbg)))
            for itr in range(len(dbg)):
                irc.debug("Iteration: %s/%s" % (str(itr), str(len(dbg))))
                irc.debug(dbg[itr])

