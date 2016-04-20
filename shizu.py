#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'BluABK <abk@blucoders.net'

# TODO: Have module-specific commands loaded from the modules themselves, not shizu.py's command()
# TODO: Support multiple IRC channels
# TODO: Support multiple IRC Servers
# TODO: Support SSL
# TODO: Implement command to trigger server-side permission-sentinel.sh - and assign this to a server-side features mod
# TODO: Add try and SomeReasonableExceptionHandler across code

# Import necessary modules
import socket  # A rather *useful* network tool
import time  # For time-based greeting functionality
import re  # Regex for the win.
import ConfigParser
from random import randint
# from subprocess import check_output
from subprocess import *
from collections import deque
import os
import unicodedata
import sys # Sys.exit in sigint handler
import signal # sigint handler
import traceback # traceback.print_exc()

# Project-specific modules
import colours as clr

clr_selection = deque([clr.green, clr.red, clr.blue, clr.purple, clr.cyan, clr.white])

# hawken proposal thing:
#def try_import(module_name):
#    try:
#        return __import__(module_name)
#    except ImportError:
#        print "[shizu/import]:\t ERROR: Unable to import %s, expect issues!" % module_name
#        return None
#    except Exception as shenanigans:
#        print shenanigans
#        return None

class Config:  # Shizu's config class # TODO: Add ConfigParser for writing changes to config.ini
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read('config.ini')

    def server(self):
        return str(self.config.get('irc', 'server'))

    def spass(self):
        return str(self.config.get('irc', 'password'))

    def port(self):
        return int(self.config.get('irc', 'port'))

    def chan(self):
        return str(self.config.get('irc', 'channel'))

    def nick(self):
        return str(self.config.get('irc', 'nickname'))

    def realname(self):
        return str(self.config.get('irc', 'real name'))

    def has_oper(self):
        try:
            if self.config.has_option('irc', 'oper name') and self.config.has_option('irc', 'oper password'):
                if self.oper_pass() != "" and self.oper_name() != "":
                    return True
            else:
                return False
        except:
            return False

    def oper_name(self):
        return str(self.config.get('irc', 'oper name'))

    def oper_pass(self):
        return str(self.config.get('irc', 'oper password'))

    def cmdsym(self):
        return str(self.config.get('irc', 'cmdsymbol'))

    def quitmsg(self):
        return str(self.config.get('irc', 'quit-message'))

    def quitpro(self):
        return str(self.config.get('irc', 'quit-protection'))

    def proxy_nicks(self):
        # try:
        return_dbg = self.config.get('irc', 'proxy-users')
        return return_dbg

    #    except ConfigParser.NoSectionError:
    #        return "That section does not seem to exist"
    #    except ConfigParser.NoOptionError:
    #        return "Option does not seem to exist"

    def su(self):
        return str(self.config.get('users', 'superusers'))

    def nspass(self):
        return str(self.config.get('nickserv', 'password'))

    def backlog(self):
        return str(self.config.getint('irc', 'backlog-limit'))

    def triggers_words(self):
        return str(self.config.get('triggers', 'words'))

    def triggers_badwords(self):
        return str(self.config.get('triggers', 'badwords'))

    def triggers_ignorednicks(self):
        return str(self.config.get('triggers', 'ignored-nicks'))

    def commands_ignorednicks(self):
        return str(self.config.get('commands', 'ignored-nicks'))

    def chk_command_perms(self, user, inst):
        try:
            allowed = str(self.config.get('custom-cmd-cfg', inst))
            if user in allowed:
                return True
            else:
                return False
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def chk_trigger_perms(self, user, inst):
        try:
            allowed = str(self.config.get('custom-trg-cfg', inst))
            if user in allowed:
                return True
            else:
                return False
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def add_command(self, name, function):
        try:
            self.config.read('config.ini')
            self.config.set('custom-cmd', name, function)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def add_trigger(self, name, function):
        try:
            self.config.read('config.ini')
            self.config.set('custom-trg', name, function)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def add_rawcommand(self, name, function):
        try:
            self.config.read('config.ini')
            self.config.set('custom-rawcmd', name, function)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def del_command(self, name):
        try:
            self.config.read('config.ini')
            self.config.remove_option('custom-cmd', name)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
                # return self.config.remove_option('custom-cmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def del_trigger(self, name):
        try:
            self.config.read('config.ini')
            self.config.remove_option('custom-trg', name)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
                # return self.config.remove_option('custom-cmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def del_rawcommand(self, name):
        try:
            self.config.read('config.ini')
            self.config.remove_option('custom-rawcmd', name)
            with open('config.ini', 'wb') as configfile:
                self.config.write(configfile)
                # return self.config.remove_option('custom-rawcmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def get_command(self, name):
        try:
            return str(self.config.get('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def get_trigger(self, name):
        try:
            return str(self.config.get('custom-trg', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def get_rawcommand(self, name):
        try:
            return str(self.config.get('custom-rawcmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def chk_command(self, name):
        try:
            return str(self.config.has_option('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def chk_trigger(self, name):
        try:
            return str(self.config.has_option('custom-trg', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def chk_rawcommand(self, name):
        try:
            return str(self.config.has_option('custom-rawcmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_command(self):
        try:
            return self.config.items('custom-cmd')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_trigger(self):
        try:
            return self.config.items('custom-trg')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_rawcommand(self):
        try:
            return self.config.items('custom-rawcmd')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_command_option(self):
        try:
            optlist = list()
            for item in self.config.items('custom-cmd'):
                optlist.append(item[0])
            return optlist
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_rawcommand_option(self):
        try:
            optlist = list()
            for item in self.config.items('custom-rawcmd'):
                optlist.append(item[0])
            return optlist
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"

    def lst_trigger_option(self):
        try:
            optlist = list()
            for item in self.config.items('custom-trg'):
                optlist.append(item[0])
            return optlist
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
            # except:
            #    return "An unknown exception occurred"


def ian(s):  # is a number
    try:
        int(s)
        return True
    except ValueError:
        return False


def debug(msg, irc):
    irc.sendraw("PRIVMSG %s :DEBUG: %s\r\n" % (cfg.chan(), msg))


def getgreeting(greeter, irc):
    t = int(time.strftime("%H"))

    if t >= 17 or t < 4:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    elif t <= -1:
        debug("Negative time returned", irc)
        greeting = "ohi"
    else:
        debug("Time returned had no valid integer value.", irc)
        greeting = "ohi"

    return "%s %s~" % (greeting, greeter)


def replay(lines, chan, direction, irc):
    if direction == 0:
        to_send = ircbacklog[-lines:]
    elif direction == 1:
        to_send = ircbacklog_in[-lines:]
    elif direction == 2:
        to_send = ircbacklog_out[-lines:]
    else:
        to_send = ircbacklog[-lines:]
        irc.sendmsg("DERP invalid direction! Defaulting to duplex", chan)

    for m in to_send:
        irc.sendmsg(m, chan)

def ignored_nick(section, usernick):
    if section == "commands":
        pattern = re.compile(cfg.commands_ignorednicks(), flags=re.IGNORECASE)
        matches = re.match(pattern, usernick)
        try:
            if matches.group(0) != "":  # If the usernick is in ignorelist
                return True
        except AttributeError:
            return False
        return False

    elif section == "triggers":
        pattern = re.compile(cfg.triggers_ignorednicks(), flags=re.IGNORECASE)
        matches = re.match(pattern, usernick)
        try:
            if matches.group(0) != "":  # If the usernick is in ignorelist
                return True
        except AttributeError:
            return False
        return False


def date():
    try:
        return check_output("date", shell=True)
    except (OSError, CalledProcessError) as ex:
        return "Execution failed due to: %s" % str(ex.message)


def ddate():
    try:
        return check_output("ddate", shell=True)
    except (OSError, CalledProcessError) as ex:
        return "Execution failed due to: %s" % str(ex.message)


def whois(user, selection, raw_in, irc):
    global ircbacklog, ircbacklog_out
    irc.sendraw("WHOIS %s\n" % user)
    data = list()

    prevmsg = ""
    msgcount = 0
    host, channels, server, oper, identified, connection, idle = None

    for n in xrange(len(ircbacklog)):
        # nyaa = str(ircbacklog[n])
        nyaa = str(raw_in)

        if nyaa != prevmsg:
            print("RAW: %s\n" % nyaa)
        else:
            msgcount += 1

        prevmsg = nyaa

        # As long as current msg isn't end of /WHOIS
        if nyaa.find("318 * %s %s" % (cfg.nick(), user)) == -1:
            if nyaa.find("311 * %s %s" % (cfg.nick(), user)) != -1:
                host = nyaa
                data.append(host)
                print(str(host) + "\n")
            elif nyaa.find("319 * %s %s" % (cfg.nick(), user)) != -1:
                channels = nyaa
                data.append(channels)
                print(str(channels) + "\n")
            elif nyaa.find("312 * %s %s" % (cfg.nick(), user)) != -1:
                server = nyaa
                data.append(server)
                print(str(server) + "\n")
            elif nyaa.find("313 * %s %s" % (cfg.nick(), user)) != -1:
                oper = nyaa
                data.append(oper)
                print(str(oper) + "\n")
            elif nyaa.find("330 * %s %s" % (cfg.nick(), user)) != -1:
                identified = nyaa
                data.append(identified)
                print(str(identified) + "\n")
            elif nyaa.find("671 * %s %s" % (cfg.nick(), user)) != -1:
                connection = nyaa
                data.append(connection)
                print(str(connection) + "\n")
            elif nyaa.find("317 * %s %s" % (cfg.nick(), user)) != -1:
                idle = nyaa
                data.append(idle)
                print(str(idle) + "\n")
        else:
            break

    if msgcount > 0:
        print("Previous message repeated %s times\n" % msgcount)

    try:
        if selection == "host":
            return host
        elif selection == "channels":
            return channels
        elif selection == "server":
            return server
        elif selection == "oper":
            return oper
        elif selection == "identified":
            return identified
        elif selection == "connection":
            return connection
        elif selection == "idle":
            return idle
    except NameError:
        return data


# Verify identity of user
def check_id(user, facility, raw_in, irc):
    # Check if user is identified with nickserv
    print("Checking ID...\n")
    if facility == "identified":
        # irc.sendmsg("facility = id", chan)
        chk = whois(user, "identified", raw_in, irc)
        print(chk)
        if len(chk) > 0:
            if chk.find("is logged in as") != -1:
                print("logged in detected in WHOIS\n")
            if chk.find(user) != -1:
                print("user detected in WHOIS\n")
            if chk.find("is logged in as") != -1 and chk.find(user) != -1:
                print("TRUE\n")
                return True
            else:
                print("DEBUG: FALSE\n")
                return False
        else:
            print("Oh dear, that response seem rather empty...\n")
    else:
        print("Whoa whoa whoa, calm down.\n")


def add_custom_cmd(name, function, usernick):
    can_add = False
    if usernick in cfg.su():
        can_add = True
    check_everyone = cfg.chk_command_perms("everyone", "add-allow")
    if check_everyone:
        can_add = True

    # irc.sendmsg("DEBUG: %s" % check_everyone, chan)

    if can_add:
        print str(function)
        print "Adding custom command: %s with function %s, requested by %s" % (name, function, usernick)
        print cfg.chk_command(name)
        # if name not in commandsavail and cfg.chk_command(name) is False:
        collision = False
        if name in commandsavail:
            collision = True

        print "collision is %s" % collision
        # if collision is False and cfg.chk_command(name) is False:
        if collision is True:
            return "That name collides with something =/"
        elif cfg.chk_command(name) is True:
            return "That name collides with something =/"
        else:
            test = cfg.add_command(name, function)
            #        test = add_command(name, function)
            if isinstance(test, str):
                return test
            else:
                return "Command %s added successfully! ^_^" % name


def add_custom_rawcmd(name, function, usernick):
    if usernick.lower() == "bluabk":
        print str(function)
        print "Adding custom command: %s with function %s, requested by %s" % (name, function, usernick)
        print cfg.chk_rawcommand(name)
        # if name not in commandsavail and cfg.chk_command(name) is False:
        collision = False
        if name in commandsavail:
            collision = True

        print "collision is %s" % collision
        # if collision is False and cfg.chk_command(name) is False:
        if collision is True:
            return "That name collides with something =/"
        elif cfg.chk_rawcommand(name) is True:
            return "That name collides with something =/"
        else:
            test = cfg.add_rawcommand(name, function)
            #        test = add_command(name, function)
            if isinstance(test, str):
                return test
            else:
                return "Command %s added successfully! ^_^" % name


def add_custom_trg(name, function, usernick):
    can_add = False
    if usernick in cfg.su():
        can_add = True
    check_everyone = cfg.chk_trigger_perms("everyone", "add-allow")
    if check_everyone:
        can_add = True

    # irc.sendmsg("DEBUG: %s" % check_everyone, chan)

    if can_add:
        print str(function)
        print "Adding custom trigger: %s with function %s, requested by %s" % (name, function, usernick)
        print cfg.chk_command(name)
        # if name not in commandsavail and cfg.chk_command(name) is False:
        collision = False
        if name in cfg.triggers_words():
            collision = True

        print "collision is %s" % collision
        # if collision is False and cfg.chk_command(name) is False:
        if collision is True:
            return "That name collides with something =/"
        elif cfg.chk_trigger(name) is True:
            return "That name collides with something =/"
        else:
            test = cfg.add_trigger(name, function)
            #        test = add_command(name, function)
            if isinstance(test, str):
                return test
            else:
                return "Trigger %s added successfully! ^_^" % name


def del_custom_cmd(name, usernick):
    can_del = False
    if usernick in cfg.su():
        can_del = True
    check_everyone = cfg.chk_command_perms("everyone", "del-allow")
    if check_everyone:
        can_del = True

    if can_del:  # and cfg.chk_command(name) is True:
        cfg.del_command(name)
        return "Command removed"
    else:
        return "Unable to remove given command"


def del_custom_rawcmd(name, usernick):
    if usernick.lower() == "bluabk":
        cfg.del_rawcommand(name)
        return "Command removed"
    else:
        return "Unable to remove given command"


def del_custom_trg(name, usernick):
    can_del = False
    if usernick in cfg.su():
        can_del = True
    check_everyone = cfg.chk_trigger_perms("everyone", "del-allow")
    if check_everyone:
        can_del = True

    if can_del:  # and cfg.chk_command(name) is True:
        cfg.del_trigger(name)
        return "Trigger removed"
    else:
        return "Unable to remove given trigger"


def custom_command(name, chan, irc):
    irc.sendmsg(cfg.get_command(name), chan)


def custom_trigger(name, chan, irc):
    irc.sendmsg(cfg.get_trigger(name), chan, irc)


def custom_rawcommand(cmd, usernick, chan, irc):
    if usernick.lower() == "bluabk":
        c = str(cfg.get_rawcommand(cmd[0]))
        print "Read command from file: %s" % c
        if "$chan" in c:
            c = c.replace("$chan", chan)
            print "replaced $chan var occurrences with %s" % chan
        if "$nick" in c and len(cmd) > 1:
            c = c.replace("$nick", cmd[1])
        print "Sending command as raw: %s" % c
        c += "\r\n"
        irc.sendraw(c)


def version():
    # c_date = str(check_output("git show -s --format=%ci", shell=True)).strip("\n")
    # c_hash_short = str(check_output("git rev-parse --short HEAD", shell=True)).strip("\n")
    # retv = c_date + " (" + c_hash_short + ")"
    retv = str(check_output("git log -n 1 --pretty=format:'%h - %an, %ar: %s [' --shortstat", shell=True))
    retv = retv.split('\n')[0][0:] + retv.split('\n')[1][1:] + ']'
    print(retv)
    return retv


def nickname_proxy(irc_line):
    """Takes a proxy/relay user and returns the actual usernick"""
    # Case1 : Telegram relay
    global telegram_cur_nick
    real_nick = None
    if irc_line[3][-2:] == ">:":
        # Start of a continued sentence, but payload is useless to us
        # if telegram_cur_nick is None:
        telegram_cur_nick = irc_line[3].split('> ')[0][2:-2]
        msg = ""
    elif irc_line[3][1] != '<':
        # Continued sentence; doesn't start with a usernick identifier
        # TODO: Will fail is continued sentence starts with '<'
        real_nick = telegram_cur_nick
        msg = irc_line[3][1:]
    else:
        # Assume that sentence starts with a usernick
        real_nick = irc_line[3].split('> ')[0][2:]
        msg = irc_line[3].split('> ')[1]
        telegram_cur_nick = real_nick

    # Strip any fancy smancy unicode as it won't be a valid IRC nickname
    if real_nick is not None:
        real_nick = real_nick.decode('ascii', 'ignore').encode('utf-8')

    return [real_nick, msg]


def commands(usernick, msg, chan, irc):
    global watch_enabled
    # First of all, check if it is a command
    if chan[0] == "#":
        # If message starts in trigger
        if msg[:len(cfg.cmdsym())] == cfg.cmdsym():
            # Strip trigger
            msg = msg[len(cfg.cmdsym()):]
        # else it is not a command
        else:
            return

    cmd = msg.split(' ')
    # Stats
    if cmd[0].lower() in commandsavail or cmd[0].lower() in lastfm.commandsavail_short or cmd[0].lower() in \
            watch.commandsavail_short or cmd[0].lower() in cfg.lst_command_option() or cmd[0].lower() in \
            cfg.lst_rawcommand_option():
        print "stats: matched regular command"
        stats.update_cmd(cmd[0], 1)
        stats.update_user(usernick, cmd[0], 1)
    elif len(cmd) > 1:
        if cmd[0].lower() == "stats":
            print "stats: matched stats module command"
            if cmd[1] in lastfm.commandsavail:
                stats.update_cmd(('stats ' + cmd[1]), 1)
                stats.update_user(usernick, ('stats ' + cmd[1]), 1)
        elif cmd[0].lower() == "lastfm":
            print "stats: matched lastfm module command"
            if cmd[1] in lastfm.commandsavail:
                stats.update_cmd(('lastfm ' + cmd[1]), 1)
                stats.update_user(usernick, ('lastfm ' + cmd[1]), 1)
        elif cmd[0].lower() == "watch":
            print "stats: matched watch module command"
            if cmd[1] in watch.commandsavail:
                stats.update_cmd(('watch ' + cmd[1]), 1)
                stats.update_user(usernick, ('watch ' + cmd[1]), 1)
        elif cmd[0].lower() == "samba":
            print "stats: matched samba module command"
            if cmd[1] in samba.commandsavail:
                stats.update_cmd(('samba ' + cmd[1]), 1)
                stats.update_user(usernick, ('samba ' + cmd[1]), 1)

    # General commands
    if cmd[0].lower() == "awesome":
        irc.sendmsg("Everything is awesome!", chan)
    elif cmd[0].lower() == "version":
        irc.sendmsg("%s" % version(), chan)
    elif cmd[0].lower() == "nyaa":
        irc.sendmsg("Nyaa~", chan)
    elif cmd[0].lower() == "date":
        irc.sendmsg(date(), chan)
    elif cmd[0].lower() == "ddate":
        irc.sendmsg(ddate(), chan)
    elif cmd[0].lower() == "showtopic":
        topic(None, chan, irc)
        irc.sendmsg("Nyaa~", chan)
    elif cmd[0].lower() == "dump":
        try:
            if cmd[1] == "cmd":
                if len(cmd) > 1:
                    if cmd[2] == "ignorednicks":
                        irc.sendmsg("Ignored nicks: %s" % cfg.commands_ignorednicks(), chan)
            elif cmd[1] == "trg":
                if len(cmd) > 1:
                    if cmd[2] == "ignorednicks":
                        try:
                            irc.sendmsg("Ignored nicks: %s" % cfg.triggers_ignorednicks(), chan)
                        except TypeError:
                            irc.sendmsg("An error occurred, sue me", chan)
            elif cmd[1] == "lastfm":
                if len(cmd) > 1:
                    if cmd[2] == "alias":
                        # try:
                        da_list = lastfm.cfg.list_alias()
                        # for i in range(len(da_list[0])):
                        #    for item in da_list:
                        #        print item[i]
                        # print da_list
                        irc.sendmsg(da_list, chan)
                        # except:
                        #    irc.sendmsg("An error occurred, sue me", chan)
            else:
                irc.sendmsg("Available parameters for this debug function:"
                        " {cmd ignorednicks, trg ignorednicks, lastfm alias}", chan)
        except IndexError:
            irc.sendmsg("INFODUMP: Invalid argument(s)", chan)
    elif cmd[0].lower() == "kick":

        # Make sure that it is an actual user
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s: Abuse by proxy? Nice try... ಠ_ಠ" % usernick, chan)
            return

        # Check if user is authorised to do so
        for u in cfg.su().lower().split(","):
            if usernick.lower() == u:
                try:
                    try:
                        # KICK <user> <reason>
                        irc.sendraw("KICK %s %s %s\n" % (chan, cmd[1], cmd[2]))
                        return
                    except IndexError:
                        # KICK <user> <static reason> (fallback if no reason given)
                        irc.sendraw("KICK %s %s *shove*\n" % (chan, cmd[1]))
                        return
                except IndexError:
                    print("IndexError in authorisation check")
                    return

        # If all else fails, user was probably not authorised and must be punished for abuse
        irc.sendraw("KICK %s %s Backfired, oh the irony! ~\n" % (chan, usernick))

    elif cmd[0].lower() == "replay":
        # TODO not 100% sure here, debug the backlog list a little and find out if this is safe
        if len(cmd) > 2 and ian(cmd[1]) and int(cmd[1]) <= maxbacklog:
            try:
                if cmd[2] == "duplex":
                    replay(int(cmd[1]), chan, 0, irc)
                elif cmd[2] == "recv":
                    replay(int(cmd[1]), chan, 1, irc)
                elif cmd[2] == "send":
                    replay(int(cmd[1]), chan, 2, irc)
            except IndexError:
                irc.sendmsg("WHOA! IndexError in cmd[2] o_0", chan)
                replay(int(cmd[1]), chan, 0, irc)
        else:
            replay(maxbacklog, chan, 0, irc)
    elif cmd[0].lower() == "say":
        if len(cmd) > 1:
            # Secure outgoing message
            if (re.match(r"^\x01[^\s]*", cmd[1]) is None) and (re.match(r"^![^\s]+", cmd[1]) is None):
                irc.sendmsg(" ".join(cmd[1:]), chan)
        else:
            irc.sendmsg("Syntax: %ssay <string>" % cfg.cmdsym(), chan)
    elif cmd[0].lower() == "act":
        irc.sendmsg("\x01ACTION %s\x01" % " ".join(cmd[1:]), chan)
    elif cmd[0].lower() == "join":
        # Ability to join multiple channels
        newchans = cmd[1:]
        for newchan in newchans:
            if newchan[0] == '#':
                irc.sendraw("JOIN %s\r\n" % newchan)
            else:
                irc.sendraw("JOIN #%s\r\n" % newchan)
    elif cmd[0].lower() == "quit" and usernick in cfg.su():  # and cmd[1] == cfg.quitpro():
        irc.quit()

    elif cmd[0].lower() == "host":
        if len(cmd) > 1:
            try:
                retval = check_output("host %s" % cmd[1], shell=True)
                # for line in retval:
                #   irc.sendmsg(line, chan)
                irc.sendmsg(retval, chan)
            except CalledProcessError:
                irc.sendmsg("Invalid argument.... (and you *know* it)", chan)

    # Help calls
    if cmd[0].lower() == "help":
        try:
            if cmd[1] == "triggers":
                irc.sendmsg("%s: Syntax: <trigger> %s" % (usernick, cfg.nick()), chan)
                irc.sendmsg("Available triggers: %s " % cfg.triggers_words(), chan)
            elif cmd[1] == "replay":
                irc.sendmsg("%s: Syntax: %sreplay <lines> <direction>" % (usernick, cfg.cmdsym()), chan)
                irc.sendmsg("Available commands: recv, send, duplex", chan)
            elif cmd[1] == "kick":
                irc.sendmsg("%s: Syntax: %skick <user>" % (usernick, cfg.cmdsym()), chan)
            elif cmd[1] == "samba":
                if len(cmd) > 2:
                    if cmd[2] == "logins":
                        irc.sendmsg("%s: Syntax: %ssamba logins <user>" % (usernick, cfg.cmdsym()), chan)
                else:
                    for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                        irc.sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan)
            elif cmd[1] == "lastfm":
                if len(cmd) > 2:
                    if cmd[2] == "recent":
                        irc.sendmsg("%s: Syntax: %slastfm recent <user> <num>" % (usernick, cfg.cmdsym()), chan)
                    if cmd[2] == "alias":
                        irc.sendmsg("%s: Syntax: %slastfm alias [set|unset] <user>" %
                                (usernick, cfg.cmdsym()), chan)
                    if cmd[2] == "bio":
                        irc.sendmsg("%s: Syntax: %slastfm bio <artist>" %
                                (usernick, cfg.cmdsym()), chan)
                else:
                    for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                        irc.sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan)
        except IndexError:
            helpcmd(usernick, chan, irc)

    # module lastfm
    elif cmd[0].lower() == "lastfm":
        if len(cmd) > 1:
            if cmd[1] == "bio":
                if len(cmd) > 2:
                    feedback = lastfm.artist_bio(cmd[2])
                    if isinstance(feedback, str):
                        irc.sendmsg(str(feedback), chan)
                    # elif isinstance(feedback, list):
                    else:
                        for i in feedback:
                            irc.sendmsg(str(i), chan)
            elif cmd[1] == "status":
                auth = lastfm.test_connection()
                print auth
                print type(auth)

                if type(auth) is Exception:
                    irc.sendmsg(str(auth.message), chan)
                    irc.sendmsg(str(auth.details), chan)
                else:
                    auth = unicodedata.normalize('NFKD', auth).encode('ascii', 'ignore')
                    print auth
                    print type(auth)
                    net = lastfm.network.name
                    print net
                    print type(net)

                    # if type(auth) is str and type(net) is str:
                    if type(auth) is str and type(net) is str:
                        irc.sendmsg("I am currently authenticated as " + auth + " on " + net, chan)
                    elif type(auth) is str:
                        irc.sendmsg(
                            "I am currently authenticated as " + auth + " on *NO NETWORK*, how does that even work? =/",
                            chan)
                    elif net is str:
                        irc.sendmsg("I am somehow connected to " + net + ", but not authenticated... Okay then!", chan)
                    else:
                        irc.sendmsg("I am unable to query the network, is LastFM throwing a fit?", chan)
            elif cmd[1] == "alias":
                if len(cmd) > 2:
                    if cmd[2] == "set":
                        if len(cmd) > 3:
                            tmp = lastfm.add_alias(usernick, cmd[3])
                            irc.sendmsg(tmp, chan)
                    elif cmd[2] == "unset":
                        if len(cmd) > 3:
                            tmp = lastfm.del_alias(usernick)
                            irc.sendmsg(tmp, chan)
                    else:
                        tmp = lastfm.add_alias(usernick, cmd[2])
                        irc.sendmsg(tmp, chan)

            elif cmd[1] == "recent":
                default_num = 3
                # !lastfm recent nick num
                if len(cmd) > 3:
                    num = cmd[3]
                    nick = cmd[2]
                    # !lastfm recent nick num
                    try:
                        if 0 > num <= 10:
                            test = lastfm.recently_played(nick, num)
                        # !lastfm recent nick 3 (num was out of bounds)
                        else:
                            test = lastfm.recently_played(nick, default_num)
                    except TypeError:
                        test = lastfm.recently_played(nick, default_num)
                # !lastfm recent num
                elif len(cmd) > 2:
                    num = cmd[2]
                    nick = usernick
                    test = lastfm.recently_played(nick, num)
                # !lastfm recent
                else:
                    nick = usernick
                    test = lastfm.recently_played(nick, default_num)

                # Test returned data integrity
                # If the returned data is a string it is most likely an exception and should be handled as one
                if type(test) is str:
                    irc.sendmsg(test, chan)
                elif test is None:
                    irc.sendmsg("%s has not played anything in the given period" % nick, chan)
                elif test == "None":
                    irc.sendmsg("%s: No user named '%s' was found =/" % (nick, test), chan)
                else:
                    irc.sendmsg("%s has recently played:" % nick, chan)
                    for item in xrange(len(test)):
                        irc.sendmsg(str(test[item]), chan)
            # Print help
            else:
                for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                    irc.sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan)

    elif cmd[0].lower() == "ragequit":
        raise Exception("spam", "eggs")

    # Module: lastfm - shortcuts
    elif cmd[0].lower() == "np":
        try:
            test = lastfm.now_playing(cmd[1])
            if test is None:
                irc.sendmsg("%s is not currently playing anything" % cmd[1], chan)
            elif test == "None":
                irc.sendmsg("No user named '%s' was found =/" % cmd[1], chan)
            elif test == "timeout":
                irc.sendmsg("Request timed out =/", chan)
            else:
                irc.sendmsg("%s is currently playing: %s" % (cmd[1], test), chan)
        except IndexError:
            test = lastfm.now_playing(usernick)
            if test is None:
                irc.sendmsg("%s is not currently playing anything" % usernick, chan)
            elif test == "None":
                irc.sendmsg("%s: No user named '%s' was found =/ "
                        "You can set an alias with !lastfm set alias <lastfmuser>" % (usernick, test), chan)
            elif test == "timeout":
                irc.sendmsg("Request timed out =/", chan)
            else:
                irc.sendmsg("%s is currently playing: %s" % (usernick, test), chan)

    elif cmd[0].lower() == "npt":
        try:
            irc.sendmsg("%s is currently playing; %s" % (usernick, lastfm.test_playing(cmd[1])), chan)
        except IndexError:
            irc.sendmsg("Index derp", chan)

    # Module: samba
    elif cmd[0].lower() == "samba":
        if len(cmd) > 1:
            if cmd[1] == "logins":
                irc.sendmsg(samba.get_logins(cmd[2:]), chan)
            elif cmd[1] == "np":
                irc.sendmsg(samba.get_playing(), chan)
            elif cmd[1] == "np2":
                irc.sendmsg(samba.get_playing2(), chan)
        else:
            for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                irc.sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan)

    # Debug commands
    elif cmd[0].lower() == "debug":
        if len(cmd) >= 2 and cmd[1] == "logins":
            dbg = samba.get_logins(cmd[2:])
            debug("Passed variable of length:" + str(len(dbg)), irc)
            for itr in range(len(dbg)):
                debug("Iteration: %s/%s" % (str(itr), str(len(dbg))), irc)
                debug(dbg[itr], irc)

    # Custom commands
    elif cmd[0].lower() == "addcommand":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            arg = list()
            for item in xrange(len(cmd)):
                if item > 1:
                    if item != "\n":
                        arg.append(cmd[item])
                        print "arg = %s" % arg
            fstr = " ".join(str(x) for x in arg)
            ret = add_custom_cmd(str(cmd[1]), fstr, usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0].lower() == "removecommand":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            ret = del_custom_cmd(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0].lower() == "addrawcommand" and usernick.lower() == "bluabk":
        if len(cmd) > 1:
            arg = list()
            for item in xrange(len(cmd)):
                if item > 1:
                    if item != "\n":
                        arg.append(cmd[item])
                        print "arg = %s" % arg
            fstr = " ".join(str(x) for x in arg)
            ret = add_custom_rawcmd(str(cmd[1]), fstr, usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0].lower() == "removerawcommand" and usernick.lower() == "bluabk":
        if len(cmd) > 1:
            ret = del_custom_rawcmd(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0].lower() == "listcustom":
        string_list = ""
        for item in cfg.lst_command():
            string_list += (item[0] + " ")
        for item in cfg.lst_rawcommand():
            string_list += (item[0] + "* ")
        irc.sendmsg(string_list, chan)

    # Custom triggers
    elif cmd[0].lower() == "addtrigger":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            arg = list()
            for item in xrange(len(cmd)):
                if item > 1:
                    if item != "\n":
                        arg.append(cmd[item])
                        print "arg = %s" % arg
            fstr = " ".join(str(x) for x in arg)
            ret = add_custom_trg(str(cmd[1]), fstr, usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0].lower() == "removetrigger":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            ret = del_custom_trg(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    # TODO: Raw triggers

    elif cmd[0].lower() == "customtriggers":
        string_list = ""
        for item in cfg.lst_trigger():
            string_list += (item[0] + " ")
        irc.sendmsg(string_list, chan)


    # Module: Watch
    elif cmd[0].lower() == "watch":
        if len(cmd) > 1:
            if cmd[1] == "enable":
                watch_enabled = True
                irc.sendmsg("Watch notifications enabled.", chan)

            elif cmd[1] == "disable":
                watch_enabled = False
                irc.sendmsg("Watch notifications disabled.", chan)

            elif cmd[1] == "limit":
                print "watch: Setting watchlimit to %s" % cmd[2]
                watch.set_notify_limit(cmd[2])
                irc.sendmsg("Watch notifications limit set to %s" % cmd[2], chan)
        else:
            for item in xrange(len(atch.helpcmd(cfg.cmdsym()))):
                irc.sendmsg(str(watch.helpcmd(cfg.cmdsym())[item]), chan)

    # Module: Stats
    elif cmd[0].lower() == "stats":
        if len(cmd) > 1:
            if cmd[1] == "cmd" or cmd[1] == "command":
                if len(cmd) > 2:
                    irc.sendmsg(str(stats.get_cmd(cmd[2])), chan)
                else:
                    cmd_list = stats.get_cmd_all()
                    cmd_string = ""
                    cnt = 0
                    for item in cmd_list:
                        cmd_string += ("%s: %s" % (item[0], item[1]))
                        cnt += 1
                        if cnt <= len(cmd_list)-1:
                            cmd_string += ", "
                        cmd_string.strip('\n')
                    print repr(cmd_string)
                    irc.sendmsg(cmd_list, chan)

            elif cmd[1] == "user":
                # TODO: Code user stats get command
                irc.sendmsg("Dummy function", chan)
        else:
            for item in xrange(len(stats.helpcmd(cfg.cmdsym()))):
                irc.sendmsg(str(stats.helpcmd(cfg.cmdsym())[item]), chan)

    elif cmd[0].lower() in cfg.lst_command_option():
        print "Executing custom command"
        custom_command(cmd[0].lower(), chan, irc)

    elif cmd[0].lower() in cfg.lst_rawcommand_option() and usernick in cfg.su():
        print "Executing custom rawcommand"
        custom_rawcommand(cmd, usernick, chan, irc)

    # Module: YouTube
    elif cmd[0].lower() == "ytt" and module_exists("modules.youtube"):
        if len(cmd) > 1:
            if cmd[1].lower() == "trigger":
                new_state = youtube.toggle_trigger()
                if new_state is True:
                    return irc.sendmsg("YouTube Title: Print urls as they appear (trigger mode)", chan)
                else:
                    return irc.sendmsg("YouTube Title: Print urls if asked to (command mode)", chan)
        # Command mode (see triggers() for trigger mode)
        if youtube.get_url() is not None and youtube.get_trigger() is False:
            return irc.sendmsg(youtube.printable_title(fancy=False), chan)

    # Private Module: yr
    elif cmd[0].lower() == "yr" and module_exists("weather"):
        kittens = True
        if len(cmd) > 1:
            if cmd[1] == "extreme":
                if len(cmd) > 2:
                    extreme = yr.find_extreme_places(info=True, limit=int(cmd[2]))

                else:
                    extreme = yr.find_extreme_places(info=True, limit=10)

                irc.sendmsg("%s: %02d C & %s: %02d C" % (
                    extreme[0][0], extreme[0][1], extreme[1][0], extreme[1][1]), chan)
                return

            try:
                forecast = yr.weather_update(" ".join(map(str, cmd[1:])), hour=time.localtime().tm_hour,
                                             minute=time.localtime().tm_min, debug=kittens)
                for item in cmd:
                    if '@' in item:
                        loc = " ".join(map(str, cmd[1:]))
                        t = re.sub(r'\s+', "", loc[loc.find('@') + 1:len(loc)])[0:5].split(':')
                        forecast = yr.weather_update(loc[0:loc.find('@')].strip(' '),
                                                     hour=int(t[0]), minute=int(t[1]), debug=kittens)
                        break

                prev = forecast
                print forecast
                if forecast is not None:
                    irc.sendmsg(forecast, chan)
                elif prev is not None:
                    irc.sendmsg(forecast, chan)
                else:
                    irc.sendmsg("No such weather station", chan)
            except:
                irc.sendmsg("https://www.konata.us/nope.gif", chan)


def triggers(usernick, msg, chan, irc):
    greet_pat = re.compile((cfg.triggers_words() + " "), flags=re.IGNORECASE)
    greet_match = re.match(greet_pat, msg)
    nick_match = False
    # TODO: HACK: Actually regex match against msg having exactly triggers_words() + cfg.nick()
    for s in msg.split(" "):
        if s == cfg.nick():
            nick_match = True

    """Greeting"""
    try:
        # if matches.group(0) != "":  # If someone greets me, I will greet back.
        if greet_match and nick_match:
            irc.sendmsg((getgreeting(usernick, irc)), chan)
    except AttributeError:
        return

    """YouTube Title"""
    if module_exists("modules.youtube"):
        if youtube.get_url() is not None and youtube.get_trigger() is True:
            irc.sendmsg(youtube.printable_title(fancy=False), chan)

    # Custom Triggers
    if msg.lower() in cfg.lst_trigger_option():
        print "Executing custom trigger"
        custom_trigger(msg.lower(), chan, irc)


def listeners(usernick, msg, chan, irc):
    if module_exists("modules.youtube"):
        youtube.parse_url(msg)


def watch_notify(files, chan, msg, irc):
    for item in files:
        irc.sendmsg("%s %s" % (msg, item), chan)


def watch_notify_moved(files, chan, irc):
    # index = 0
    # strings = list()
    # for li in files:
    # for index in xrange(li[0]):

    # lame ass hack
    for item in files:
        irc.sendmsg(item, chan)


def helpcmd(user, chan, irc):
    irc.sendmsg("%s: Syntax: %scommand help arg1..argN" % (user, cfg.cmdsym()), chan)
    irc.sendmsg("Available commands: %s, %s (* command contains sub-commands)" %
            (commandsavail, modulesavail), chan)


def topic(newtopic, chan, irc):
    if newtopic is None:
        irc.sendraw("TOPIC %s\n" % chan)



class Client:
    def __init__(self):
        print "Spawned client instance"

        # Connect to the the server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((cfg.server(), cfg.port()))
        # Send password before registration [RFC2812 section-3.1.1 Password message]
        if cfg.spass() != "":
            self.sendraw("PASS " + cfg.spass() + "\n")
        # Register with the server [RFC2812 section-3.1 Connection Registration]
        self.sendraw("NICK " + cfg.nick() + "\n")
        self.sendraw("USER %s %s %s :%s\n" % (cfg.nick(), "0", "*", cfg.realname()))

    def eventloop(self):
        global ircbacklog, ircbacklog_in
        print "Entering event loop"
        i = 1
        # if module_exists("weather"):
        #    yr_init()
        for recvraw in self.sock.makefile():
            if not running:
                break

            if recvraw == '':
                continue

            recvmsg = self.raw_parse(recvraw)

            ircbacklog.append(recvraw)

            if len(ircbacklog) > maxbacklog:
                # Delete first entry
                ircbacklog = ircbacklog[1:]

            ircbacklog_in.append(recvraw)

            if len(ircbacklog_in) > maxbacklog:
                # Delete first entry
                ircbacklog_in = ircbacklog_in[1:]

            ircmsg = recvraw.strip("\n\r")  # Remove protocol junk (linebreaks and return carriage)
            ircmsg = ircmsg.lstrip(":")  # Remove first colon. Useless, waste of space >_<
            print("<-- %s" % ircmsg)  # Print received data

            ircparts = re.split("\s", ircmsg, 3)

            if ircparts[0] == '':
                continue

            if recvraw.find("433 * %s :Nickname is already in use." % cfg.nick()) != -1:
                self.sendraw("NICK " + (cfg.nick() + "|" + str(randint(0, 256))) + "\n")

            if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
                self.ping()

            if ircmsg.find("NOTICE %s :This nickname is registered" % cfg.nick()) != -1:
                self.sendraw("PRIVMSG NickServ :identify %s\r\n" % cfg.nspass())

            if ircmsg.find("NOTICE Auth :Welcome") != -1:
                if cfg.has_oper():
                    self.sendraw("OPER %s %s\n" % (cfg.oper_name(), cfg.oper_pass()))
                self.join(cfg.chan())

            # Run some checks

            # Rejoin on kick
            # TODO: Make optional and abbreviate into methods
            if ircmsg.find("KICK #") != -1:
                # TODO: HACK: Rejoin all channels
                self.join(cfg.chan())

            if ircparts[1] != '' and ircparts[1] == "PRIVMSG":
                message = ircparts[3].lstrip(":")

                tmpusernick = ircparts[0].split('!')[0]
                # Check is message was received via proxy nickname
                if tmpusernick.lower() in cfg.proxy_nicks().split(','):
                    print "DBG: nickname_proxy(%s)" % ircparts
                    tmp_chk = nickname_proxy(ircparts)
                    print "DBG: tmp_chk = %s" % tmp_chk
                    if tmp_chk[0] is not None:
                        print "DBG: tmp_chk != None"
                        tmpusernick = tmp_chk[0]
                        message = tmp_chk[1]

                channel = ircparts[2]
                if channel[0] != '#':
                    channel = tmpusernick
                try:
                    commands(tmpusernick, message, channel, self)
                except Exception as e:
                    sendmsg(e, channel, self.sock)
                    traceback.print_exc()
                try:
                    listeners(tmpusernick, message, channel, self)
                except Exception as e:
                    sendmsg(e, channel, self.sock)
                try:
                    triggers(tmpusernick, message, channel, self)
                except Exception as e:
                    sendmsg(e, channel, self.sock)

                if watch.check_added():
                    if watch_enabled:
                        if len(watch.get_added()) <= watch.notify_limit():
                            watch_notify(watch.get_added(), watch.notify_chan(), watch.cfg.msg_add(), self.sock)
                            for test in watch.get_added():
                                print ("\033[94mNotified: %s\033[0m" % test)
                        else:
                            cap_list = list()
                            for item in watch.get_added()[0:(watch.notify_limit())]:
                                cap_list.append(item)

                            cap_list[watch.notify_limit() - 1] += \
                                " ... and " + str(len(watch.get_added()) - watch.notify_limit()) + " more unlisted entries"
                            watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_add(), self.sock)
                    else:
                        for test in watch.get_added():
                            print ("\033[94mIgnored notify: %s\033[0m" % test)

                    watch.clear_added()

                if watch.check_erased():
                    if watch_enabled:
                        if len(watch.get_erased()) <= watch.notify_limit():
                            watch_notify(watch.get_erased(), watch.notify_chan(), watch.cfg.msg_del(), self.sock)
                            print "Debug del sign is %s" % watch.cfg.msg_del()
                            for test in watch.get_erased():
                                print ("\033[94mNotified: %s\033[0m" % test)
                        else:
                            cap_list = list()
                            for item in watch.get_erased()[0:(watch.notify_limit())]:
                                cap_list.append(item)

                            cap_list[watch.notify_limit() - 1] += \
                                " ... and " + str(len(watch.get_erased()) - watch.notify_limit()) + " more unlisted entries"
                            print "Debug2 del sign is %s" % watch.cfg.msg_del()
                            watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_del(), self.sock)
                    else:
                        for test in watch.get_erased():
                            print ("\033[94mIgnored notify: %s\033[0m" % test)

                    watch.clear_erased()

                if watch.check_moved():
                    if watch_enabled:
                        if len(watch.get_moved()) <= watch.notify_limit():
                            watch_notify_moved(watch.get_moved(), watch.notify_chan(), self.sock)
                            for test in watch.get_moved():
                                print ("\033[94mNotified: %s\033[0m" % test)
                        else:
                            cap_list = list()
                            for item in watch.get_moved()[0:(watch.notify_limit())]:
                                cap_list.append(item)

                            cap_list[watch.notify_limit() - 1] += \
                                " ... and " + str(len(watch.get_moved()) - watch.notify_limit()) + " more unlisted entries"
                            watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_mov(), self.sock)

                    watch.clear_moved()

            # And the tick goes on...
            i += 1

        # See ya!
        self.quit()

    def quit(self):
        self.sendraw("QUIT %s\r\n" % cfg.quitmsg())
        self.sock.close()

    def join(self, chan):
        self.sendraw("JOIN " + chan + "\n")

    def sendraw(self, buf):
        global ircbacklog_out
        self.sock.sendall(buf)
        ircbacklog_out.append(buf)
        print "--> %s" % buf

    def ping(self):
        self.sendraw("PONG :Pong\n")

    def raw_parse(self, raw):
        msg = {
            "to": None,
            "cmd": None,
            "args": [],
            "line": None
        }
        #import sys
        #module_shutdown()
        #sys.exit(1)

    def sendmsg(self, msg, chan):
        global ircbacklog_out
        try:
            if isinstance(msg, basestring):
                try:
                    data = "PRIVMSG %s :%s\r\n" % (chan, msg)
                    self.sendraw(data)
                except ValueError as ve:
                    data = "PRIVMSG %s :%s\r\n" % (chan, "sendmsg(): %s" % ve)
                    self.sendraw(data)
            else:
                # Don't check, errors from here are raised
                for item in msg:
                    self.sendmsg(item, chan)
        except TypeError as te:
            data = "PRIVMSG %s :A TypeError occurred, that's annoying: %s\r\n" % (chan, te)
            self.sendraw(data)
        except Exception as ex:
            data = "PRIVMSG %s :An Exception occurred, that's annoying: %s\r\n" % (chan, ex)
            self.sendraw(data)

def signal_exit(sig, frame):
    # No double-exiting
    signal.signal(signal.SIGINT,  signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    print "Caught signal, exiting!"
    instance.sendraw("QUIT :^C^C^C^C^C^C^C^C O.o\n")
    instance.sock.close()
    module_shutdown()
    sys.exit(0)


# ============== MODULE CODE ======================

def module_exists(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        print "[shizu/import]:\t ERROR: Unable to import %s, expect issues!" % module_name
        return False
    except Exception as shenanigans:
        print shenanigans
        return False

def module_start():
    watch.start()

def module_shutdown():
    watch.shutdown()


if module_exists("modules.samba"):
    import modules.samba as samba # for server-side samba functionality
if module_exists("modules.lastfm"):
    import modules.lastfm as lastfm
if module_exists("modules.watch"):
    import modules.watch as watch
if module_exists("modules.stats"):
    import modules.stats as stats
if module_exists("modules.youtube"):
    import modules.youtube as youtube
if module_exists("modules.weather"):
    import modules.weather as yr


# Global variables

my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.yellow
ircbacklog = list()
ircbacklog_in = list()
ircbacklog_out = list()
running = True
watch_enabled = True
commandsavail = "awesome, nyaa, help, quit*, triggers, replay*, say, act, kick*, date, ddate, version"
modulesavail = "samba*"
telegram_cur_nick = None

# Variables declared by config file
cfg = Config()
maxbacklog = int(cfg.backlog())

# TODO instance will in the future be a list of all connections
instance = Client()


# Main()
if __name__ == "__main__":

    module_start()

    signal.signal(signal.SIGINT,  signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    try:
        instance.eventloop()
    except Exception as e:
        module_shutdown()
        raise

    module_shutdown()
