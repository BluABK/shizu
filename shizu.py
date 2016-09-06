#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import necessary modules
import ConfigParser
import re  # Regex for the win.
import socket  # A rather *useful* network tool
import ssl     # Secure Socket Layer
import time  # For time-based greeting functionality
from random import randint

# from subprocess import check_output
from subprocess import *
from collections import deque
import os
import sys  # Sys.exit in sigint handler
import signal  # sigint handler
import traceback  # traceback.print_exc()

# Project-specific modules
import colours as clr

"""
README module interface:
    help(user, chan)            generate help information, see module_help()
    dump(user, chan, cmd, irc)  dump data from a module
    commands()                  see module_commands.
    listener(nick, chan, msg, irc) Triggerless actions go here
    start()                     Initialize the module (To be removed?)
    shutdown()                  Destruct a module
    ping(irc)                   Called regularly (default: 1 sec)

Debug function_exists if you suspect there are undocumented functionality here
"""

__author__ = 'BluABK <abk@blucoders.net'

clr_selection = deque([clr.green, clr.red, clr.blue, clr.purple, clr.cyan, clr.white])


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.use_ssl = False
        self.config.read('config.ini')

    def ssl(self):
        return self.use_ssl

    def server(self):
        if self.config.has_option('irc', 'server'):
            return str(self.config.get('irc', 'server'))
        else:
            self.config.set('irc', 'server')

    def spass(self):
        if self.config.has_option('irc', 'password'):
            return str(self.config.get('irc', 'password'))
        else:
            self.config.set('irc', 'password')

    def port(self):
        if self.config.has_option('irc', 'port'):
            port = self.config.get('irc', 'port')
            if '+' in port:
                self.use_ssl = True
                port = port.strip('+')

            return int(port)
        else:
            self.config.set('irc', 'port', '6667')

    def ping_interval(self):
        """ The amount of time in seconds between module_ping calls. Supports float """
        if self.config.has_option('irc', 'ping interval'):
            return int(self.config.get('irc', 'ping interval'))
        else:
            self.config.set('irc', 'ping interval')

    def chan(self):
        if self.config.has_option('irc', 'channel'):
            return str(self.config.get('irc', 'channel'))
        else:
            self.config.set('irc', 'channel')

    def nick(self):
        if self.config.has_option('irc', 'nickname'):
            return str(self.config.get('irc', 'nickname'))
        else:
            self.config.set('irc', 'nickname', 'shizu')

    def realname(self):
        if self.config.has_option('irc', 'real name'):
            return str(self.config.get('irc', 'real name'))
        else:
            self.config.set('irc', 'real name', 'Nibiiro Shizuka')

    def has_oper(self):
        try:
            if self.config.has_option('irc', 'oper name') and self.config.has_option('irc', 'oper password'):
                if self.oper_pass() != "" and self.oper_name() != "":
                    return True
            else:
                return False
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            return False

    def oper_name(self):
        if self.config.has_option('irc', 'oper name'):
            return str(self.config.get('irc', 'oper name'))

    def oper_pass(self):
        if self.config.has_option('irc', 'oper password'):
            return str(self.config.get('irc', 'oper password'))

    def cmdsym(self):
        if self.config.has_option('irc', 'cmdsymbol'):
            return str(self.config.get('irc', 'cmdsymbol'))
        else:
            self.config.set('irc', 'cmdsymbol', '!')

    def quitmsg(self):
        if self.config.has_option('irc', 'quit-message'):
            return str(self.config.get('irc', 'quit-message'))
        else:
            self.config.set('irc', 'quit-message', 'Bye!')

    def quitpro(self):
        if self.config.has_option('irc', 'quit-protection'):
            return str(self.config.get('irc', 'quit-protection'))

    def proxy_nicks(self):
        if self.config.has_option('irc', 'proxy-users'):
            return_dbg = self.config.get('irc', 'proxy-users')
            return return_dbg

    def su(self):
        if self.config.has_option('users', 'superusers'):
            return str(self.config.get('users', 'superusers'))

    def nspass(self):
        if self.config.has_option('nickserv', 'password'):
            return str(self.config.get('nickserv', 'password'))

    def backlog(self):
        if self.config.has_option('irc', 'backlog-limit'):
            return str(self.config.getint('irc', 'backlog-limit'))

    def triggers_words(self):
        if self.config.has_option('triggers', 'words'):
            return str(self.config.get('triggers', 'words'))

    def triggers_badwords(self):
        if self.config.has_option('triggers', 'badwords'):
            return str(self.config.get('triggers', 'badwords'))

    def triggers_ignorednicks(self):
        if self.config.has_option('triggers', 'ignored-nicks'):
            return str(self.config.get('triggers', 'ignored-nicks'))

    def commands_ignorednicks(self):
        if self.config.has_option('commands', 'ignored-nicks'):
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


def getgreeting(greeter, irc):
    t = int(time.strftime("%H"))

    if t >= 17 or t < 4:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    elif t <= -1:
        irc.debug("Negative time returned")
        greeting = "ohi"
    else:
        irc.debug("Time returned had no valid integer value.")
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
    irc.sendraw("WHOIS %s" % user)
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
    irc.sendmsg(cfg.get_trigger(name), chan)


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
        irc.sendraw(c)


def version():
    # c_date = str(check_output("git show -s --format=%ci", shell=True)).strip("\n")
    # c_hash_short = str(check_output("git rev-parse --short HEAD", shell=True)).strip("\n")
    # retv = c_date + " (" + c_hash_short + ")"
    retv = str(check_output("git log -n 1 --pretty=format:'%h - %an, %ar: %s [' --shortstat", shell=True))
    retv = retv.split('\n')[0][0:] + retv.split('\n')[1][1:] + ']'
    print(retv)
    return retv


def nickname_proxy(msg):
    """Takes a proxy/relay user and returns the actual usernick
    :param msg:
    """
    # Case1 : Telegram relay
    global telegram_cur_nick
    real_nick = None

    if msg["line"][-2:] == ">:":
        # Start of a continued sentence, but payload is useless to us
        # if telegram_cur_nick is None:
        telegram_cur_nick = msg["line"][1:-2]
        line = ""
    elif msg["line"][0] != '<':
        # Continued sentence; doesn't start with a usernick identifier
        # TODO: Will fail is continued sentence starts with '<'
        real_nick = telegram_cur_nick
        line = msg["line"]
    else:
        # Assume that sentence starts with a usernick
        split = msg["line"].split('> ')
        real_nick = split[0][1:]
        line = split[1]
        telegram_cur_nick = real_nick

    # Strip any fancy smancy unicode as it won't be a valid IRC nickname
    if real_nick is not None:
        real_nick = real_nick.decode('ascii', 'ignore').encode('utf-8')

    return [real_nick, line]


def commands(usernick, msg, chan, irc):
    # First of all, check if it is a command
    if chan[0] == "#":
        # If message starts in trigger
        if msg[:len(cfg.cmdsym())] == cfg.cmdsym():
            # Strip trigger
            msg = msg[len(cfg.cmdsym()):]
        # else it is not a command
        else:
            return
    else:
        return

    mod_commands = module_commands()
    cmd = msg.split(' ')
    cmd[0] = cmd[0].lower()

    if cmd[0] in mod_commands:
        # TODO: If it gets popular to spy on other commands, make an interface for this
        if "stats" in modules:
            modules["stats"].update_cmd(cmd[0], 1)
            # stats.update_user(usernick, cmd[0], 1) # TODO broken by design :(
        retv = None
        try:
            retv = mod_commands[cmd[0]](usernick, chan, cmd[1:], irc)
            print "DEBUG: mod_commands[%s](%s, %s, %s, %s): %s" % (cmd[0], usernick, chan, cmd[1:], irc, retv)
        except Exception as enp:
            if enp.message is 'LastFMNotPlaying':
                print "Caught LastFMNotPlaying Exception"
                # If user is not playing anything, verify with samba
                if "samba" in modules:
                    try:
                        retv2 = mod_commands['samba'](usernick, chan, ['np'], irc)
                        print "DEBUG: mod_commands[%s](%s, %s, %s, %s): %s" % (cmd[0], usernick, chan,
                                                                               cmd[1:], irc, retv)
                    except Exception as esmb:
                        if esmb.message is "SambaNotPlaying":
                            print "Caught SambaNotPlaying Exception (Verification mode)"
                            irc.sendmsg("%s is not playing anything." % usernick, chan)
                else:
                    print "ERROR: Samba module not available to verify NowPlaying situation"
            elif enp.message is "SambaNotPlaying":
                print "Caught SambaNotPlaying Exception"
                irc.sendmsg("%s is not playing anything." % usernick, chan)

        print "DEBUG*: mod_commands[%s](%s, %s, %s, %s): %s" % (cmd[0], usernick, chan, cmd[1:], irc, retv)
        #except cmd[0].NotPlaying as lastfm_nop:
        #    raise lastfm_nop
        return

    # General commands
    if cmd[0] == "awesome":
        irc.sendmsg("Everything is awesome!", chan)
        return
    elif cmd[0] == "version":
        irc.sendmsg("%s" % version(), chan)
        return
    elif cmd[0] == "nyaa":
        irc.sendmsg("Nyaa~", chan)
        return
    elif cmd[0] == "date":
        irc.sendmsg(date(), chan)
        return
    elif cmd[0] == "ddate":
        irc.sendmsg(ddate(), chan)
        return
    elif cmd[0] == "showtopic":
        irc.topic(None, chan)
        irc.sendmsg("Nyaa~", chan)
        return
    elif cmd[0] == "dump":
        cmd[1] = cmd[1].lower()

        if cmd[1] == "cmd":
            if len(cmd) > 1:
                if cmd[2] == "ignorednicks":
                    irc.sendmsg("Ignored nicks: %s" % cfg.commands_ignorednicks(), chan)
        elif cmd[1] == "trg":
            if len(cmd) > 1:
                if cmd[2] == "ignorednicks":
                    irc.sendmsg("Ignored nicks: %s" % cfg.triggers_ignorednicks(), chan)
        else:
            module_dump(usernick, chan, cmd[1:], irc)
        return
    elif cmd[0] == "kick":

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
                        irc.sendraw("KICK %s %s %s" % (chan, cmd[1], cmd[2]))
                        return
                    except IndexError:
                        # KICK <user> <static reason> (fallback if no reason given)
                        irc.sendraw("KICK %s %s *shove*" % (chan, cmd[1]))
                        return
                except IndexError:
                    print("IndexError in authorisation check")
                    return

        # If all else fails, user was probably not authorised and must be punished for abuse
        irc.sendraw("KICK %s %s Backfired, oh the irony! ~" % (chan, usernick))

    elif cmd[0] == "replay":
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
    elif cmd[0] == "say":
        if len(cmd) > 1:
            # Secure outgoing message
            if (re.match(r"^\x01[^\s]*", cmd[1]) is None) and (re.match(r"^![^\s]+", cmd[1]) is None):
                irc.sendmsg(" ".join(cmd[1:]), chan)
        else:
            irc.sendmsg("Syntax: %ssay <string>" % cfg.cmdsym(), chan)
    elif cmd[0] == "act":
        irc.sendmsg("\x01ACTION %s\x01" % " ".join(cmd[1:]), chan)
    elif cmd[0] == "join":
        # Ability to join multiple channels
        newchans = cmd[1:]
        for newchan in newchans:
            if newchan[0] == '#':
                irc.sendraw("JOIN %s" % newchan)
            else:
                irc.sendraw("JOIN #%s" % newchan)
    elif cmd[0] == "quit" and usernick in cfg.su():  # and cmd[1] == cfg.quitpro():
        irc.quit()

    elif cmd[0] == "host":
        if len(cmd) > 1:
            try:
                retval = check_output("host %s" % cmd[1], shell=True)
                # for line in retval:
                #   irc.sendmsg(line, chan)
                irc.sendmsg(retval, chan)
            except CalledProcessError:
                irc.sendmsg("Invalid argument.... (and you *know* it)", chan)

    # Help calls
    if cmd[0] == "help":
        # All of cmd to lower
        cmd = [x.lower() for x in cmd]

        mhelp = {
            "replay": "<lines> <direction:recv|send|duplex>",
            "kick": "<user>",
            "help": "[full command]"
        }
        mhelp = module_help(usernick, chan, mhelp)
        item = ' '.join(cmd[1:])

        if len(cmd) > 2 and cmd[1] == "triggers":
            irc.sendmsg("%s: Syntax: <trigger> %s" % (usernick, cfg.nick()), chan)
            irc.sendmsg("Available triggers: %s " % cfg.triggers_words(), chan)
        elif item in mhelp:
            irc.sendmsg(usernick + ": Syntax: " + cfg.cmdsym() + item + " " + mhelp[item], chan)
        else:
            items = [cfg.cmdsym() + x for x in mhelp.keys() + ["triggers"]]
            items.sort()
            irc.sendmsg(usernick + ": Available commands: " + ', '.join(items), chan)
        return

    elif cmd[0] == "ragequit":
        raise Exception("spam", "eggs")

    # Custom commands
    elif cmd[0] == "addcommand":
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

    elif cmd[0] == "removecommand":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            ret = del_custom_cmd(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0] == "addrawcommand" and usernick.lower() == "bluabk":
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

    elif cmd[0] == "removerawcommand" and usernick.lower() == "bluabk":
        if len(cmd) > 1:
            ret = del_custom_rawcmd(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    elif cmd[0] == "listcustom":
        string_list = ""
        for item in cfg.lst_command():
            string_list += (item[0] + " ")
        for item in cfg.lst_rawcommand():
            string_list += (item[0] + "* ")
        irc.sendmsg(string_list, chan)

    # Custom triggers
    elif cmd[0] == "addtrigger":
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

    elif cmd[0] == "removetrigger":
        if ignored_nick("commands", usernick) is True:
            irc.sendmsg("%s:ಠ_ಠ" % usernick, chan)
            return
        if len(cmd) > 1:
            ret = del_custom_trg(str(cmd[1]), usernick)
            irc.sendmsg(ret, chan)

    # TODO: Raw triggers

    elif cmd[0] == "customtriggers":
        string_list = ""
        for item in cfg.lst_trigger():
            string_list += (item[0] + " ")
        irc.sendmsg(string_list, chan)

    elif cmd[0] in cfg.lst_command_option():
        print "Executing custom command"
        custom_command(cmd[0], chan, irc)

    elif cmd[0] in cfg.lst_rawcommand_option() and usernick in cfg.su():
        print "Executing custom rawcommand"
        custom_rawcommand(cmd, usernick, chan, irc)


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

    # Custom Triggers
    if msg.lower() in cfg.lst_trigger_option():
        print "Executing custom trigger"
        custom_trigger(msg.lower(), chan, irc)


class Client:
    def __init__(self):
        cfg.port()
        print "Spawned client instance (ssl = %s)" % cfg.ssl()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if cfg.ssl():
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self.sock = context.wrap_socket(self.sock, server_hostname=cfg.server())
        self.buf = ""
        self.running = True

    def connect(self):
        # Connect to the the server
        self.sock.connect((cfg.server(), cfg.port()))
        self.sock.settimeout(cfg.ping_interval())
        # Send password before registration [RFC2812 section-3.1.1 Password message]
        if cfg.spass() != "":
            self.sendraw("PASS " + cfg.spass())
        # Register with the server [RFC2812 section-3.1 Connection Registration]
        self.sendraw("NICK " + cfg.nick())
        self.sendraw("USER %s %s %s :%s" % (cfg.nick(), "0", "*", cfg.realname()))

    def readline(self):
        # Get at least a line
        while self.buf.find("\n") == -1:
            data = self.sock.recv(65536)
            self.buf += data
        idx = self.buf.find("\n")

        # Split into line
        line = self.buf[:idx]
        # Remove \r
        if line[-1] == "\r":
            line = line[:-1]
        # Set buf
        self.buf = self.buf[idx + 1:]

        # No newlines
        return line

    def eventloop(self):
        global ircbacklog, ircbacklog_in
        print "Entering event loop"
        i = 1

        last_ping = None

        # for recvraw in self.sock.makefile():
        while self.sock and self.running:
            try:
                recvraw = self.readline()
            except (socket.timeout, ssl.SSLError):
                recvraw = None

            # Module ping()
            # The last one is for backwards jumps in time
            if last_ping is None or last_ping + cfg.ping_interval() < time.time() or time.time() < last_ping:
                last_ping = time.time()
                module_ping(self)

            if recvraw == '' or recvraw is None:
                continue

            print "<-- " + recvraw  # Print received data

            # Backlog stuff. Possible TODO: Make a class for ircbacklog or find a cooler pre-made type
            ircbacklog.append(recvraw + "\n")

            if len(ircbacklog) > maxbacklog:
                # Delete first entry
                ircbacklog = ircbacklog[1:]

            ircbacklog_in.append(recvraw + "\n")

            if len(ircbacklog_in) > maxbacklog:
                # Delete first entry
                ircbacklog_in = ircbacklog_in[1:]

            msg = self.parse_raw(recvraw)

            if msg["cmd"] == "001":
                if cfg.has_oper():
                    self.sendraw("OPER %s %s" % (cfg.oper_name(), cfg.oper_pass()))
                self.join(cfg.chan())
                continue

            if msg["cmd"] == "433":
                # TODO: cfg.nick() has to change, or we have to take a copy of it and use that instead...
                # Or we can just refuse to work if someone takes our nick. Then we also have to try to send NICK
                # if we suspect that our nick has been changed.
                self.sendraw("NICK " + (cfg.nick() + "|" + str(randint(0, 256))))
                continue

            if msg["cmd"] == "PING":
                # noinspection PyTypeChecker
                self.ping(msg["line"])
                continue

            if msg["cmd"] == "NOTICE":
                # TODO check what the full line is, and take care to check who the sender is
                if msg["line"] == "This nickname is registered" and msg["args"][0] == cfg.nick():
                    self.sendmsg("identify " + cfg.nspass(), "NickServ")

            # Run some checks

            # Rejoin on kick
            # TODO: Make optional and abbreviate into methods
            if msg["cmd"] == "KICK" and msg["args"][0] == cfg.nick():
                # TODO: HACK: Rejoin all channels
                self.join(cfg.chan())

            if msg["cmd"] == "PRIVMSG":
                try:
                    # noinspection PyTypeChecker
                    nick = msg["from"]["nick"]
                except KeyError:
                    # It's from a server, see #staff.log for example
                    # noinspection PyTypeChecker
                    nick = msg["from"]["host"]

                line = msg["line"]

                # Check is message was received via proxy nickname
                if nick.lower() in cfg.proxy_nicks().split(','):
                    tmp_chk = nickname_proxy(msg)
                    print "DBG: tmp_chk = %s" % tmp_chk
                    if tmp_chk[0] is not None:
                        print "DBG: tmp_chk != None"
                        nick = tmp_chk[0]
                        line = tmp_chk[1]

                channel = msg["args"][0]
                if channel[0] != '#':
                    channel = nick

                try:
                    commands(nick, line, channel, self)
                except Exception as e_commands:
                    self.sendmsg(e_commands, channel)
                    traceback.print_exc()

                try:
                    module_listeners(nick, channel, line, self)
                except Exception as e_module_listeners:
                    self.sendmsg(e_module_listeners, channel)
                    traceback.print_exc()

                try:
                    # TODO merge into listeners (modules cannot know the difference anyway)
                    triggers(nick, line, channel, self)
                except Exception as e_triggers:
                    self.sendmsg(e_triggers, channel)
                    traceback.print_exc()

            # And the tick goes on...
            i += 1

        # See ya!
        self.quit()

    def quit(self):
        self.sendraw("QUIT %s" % cfg.quitmsg())
        self.sock.close()
        self.running = False  # TODO: Instance attribute defined outside of __init__

    def join(self, chan):
        self.sendraw("JOIN " + chan)

    def debug(self, msg):
        self.sendraw("PRIVMSG %s :DEBUG: %s" % (cfg.chan(), msg))

    def topic(self, newtopic, chan):
        if newtopic is None:
            self.sendraw("TOPIC %s" % chan)

    def sendraw(self, buf):
        global ircbacklog_out

        if buf[-1] == "\n":
            raise ValueError("You are not supposed to send newlines to sendraw")

        self.sock.sendall(buf + "\r\n")
        ircbacklog_out.append(buf + "\n")
        print "--> %s" % buf

    def ping(self, msg="Pong"):
        self.sendraw("PONG :" + msg)

    @staticmethod
    def parse_from(line):
        off = line.find("!")
        ret = {}

        if off != -1:
            ret["nick"] = line[:off]
            tmp = line[off + 1:]
            off = tmp.find("@")
            if off == -1:
                raise ValueError("@ not found after ! (Expected something like: nick!user@host), got " + line)
            ret["user"] = tmp[:off]
            ret["host"] = tmp[off + 1:]
        else:
            ret["host"] = line
        return ret

    def parse_raw(self, raw):
        msg = {"args": []}
        raw = raw.split(' ')
        if raw[0][0] == ':':
            msg["from"] = self.parse_from(raw[0][1:])
            raw = raw[1:]

        msg["cmd"] = raw[0]
        stroffset = -1
        for i in xrange(1, len(raw)):
            if raw[i][0] == ':':
                stroffset = i
                break
            msg["args"].append(raw[i])

        if stroffset != -1:
            msg["line"] = " ".join(raw[stroffset:])[1:]

        return msg

    def sendmsg(self, msg, chan):
        global ircbacklog_out
        try:
            if isinstance(msg, basestring):
                try:
                    self.sendraw("PRIVMSG %s :%s" % (chan, msg))
                except ValueError as ve:
                    self.sendraw("PRIVMSG %s :%s" % (chan, "sendmsg(): %s" % ve))
            else:
                # Don't check, errors from here are raised
                for item in msg:
                    self.sendmsg(item, chan)
        except TypeError as te:
            self.sendraw("PRIVMSG %s :A TypeError occurred, that's annoying: %s" % (chan, te))
        except Exception as ex:
            self.sendraw("PRIVMSG %s :An Exception occurred, that's annoying: %s" % (chan, ex))


# noinspection PyUnusedLocal
def signal_exit(sig, frame):
    # No double-exiting
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    print "Caught signal, exiting!"
    instance.sendraw("QUIT :^C^C^C^C^C^C^C^C O.o")
    instance.sock.close()
    module_shutdown()
    sys.exit(0)


# ============== MODULE CODE ======================


# TODO: hawken's proposal thing:
def function_exists(thing, name):
    # TODO: Check that it actually is callable via some neat dir() things
    return name in dir(thing)


def module_import(name):
    global modules
    module_name = "modules." + name
    try:
        # noinspection PyUnusedLocal
        __module__ = __import__(module_name)
        if name in modules:
            raise ValueError("duplicate module name: " + name)
        modules[name] = eval('__module__.' + name)
        return True
    except ImportError:
        print "[shizu/import]:\t ERROR: Unable to import %s, expect issues!" % name
        return False
    except Exception as shenanigans:
        print shenanigans
        traceback.print_exc()
        return False


def module_import_list(names):
    for name in names:
        module_import(name)


def module_start():
    for name, mod in modules.iteritems():
        if function_exists(mod, "start"):
            mod.start()


def module_shutdown():
    for name, mod in modules.iteritems():
        if function_exists(mod, "shutdown"):
            mod.shutdown()


def module_ping(irc):
    """
    ping() is called regularly, default at 1 sec intervals
    :param irc:
    """
    global modules
    for name, mod in modules.iteritems():
        if function_exists(mod, "ping"):
            mod.ping(irc)


def module_listeners(nick, chan, msg, irc):
    for name, mod in modules.iteritems():
        if function_exists(mod, "listener"):
            mod.listener(nick, chan, msg, irc)


def module_commands(lst=None):
    """
    Build a dictionary of {"command": function}.
    Argument lst can be used to reserve commands for shizu itself.

    For the module:

    It is also possible to register the same function many times, for example aliases..

    def handle_a(user, chan, cmd, irc): # Handle command a
        ....
    def handle_b(user, chan, cmd, irc): # Handle command b
        ....
    def commands():     # Register the commands with shizu
       return {
            "a": handle_a,
            "b": handle_b,
            etc
       }
       :param lst:
    """
    if lst is None:
        lst = {}
    for name, mod in modules.iteritems():
        if function_exists(mod, "commands"):
            for cmd, func in mod.commands().iteritems():
                if cmd in lst:
                    print "Two modules both tried to register the command " + cmd + ", one of them is " + name
                else:
                    lst[cmd] = func
    return lst


def module_dump(usernick, chan, cmd, irc):
    if cmd[0] in modules:
        m = modules[cmd[0]]
        if function_exists(m, "dump"):
            m.dump(usernick, chan, cmd[1:], irc)


def module_help(nick, chan, usage_list=None):
    """
    The strings returned by modules should be the part of the usage after the command, i.e. for:
       lastfm alias [set|unset] <user>, the dict entry returned would be:
       "lastfm alias": "[set|unset] <user>".
       :param chan:
       :param usage_list:
       :param nick:
    """
    if usage_list is None:
        usage_list = {}
    for name, mod in modules.iteritems():
        try:
            if function_exists(mod, "help"):
                retval = mod.help(nick, chan)
                if not isinstance(retval, dict):
                    raise ValueError("help() should return a dict")

                for cmdname, usage in retval.iteritems():
                    if cmdname in usage_list:
                        raise ValueError("Command " + cmdname + " is already in use")
                    if not isinstance(usage, basestring):
                        raise ValueError("if help() returns a dict, it has to be a dict of purely strings")
                    usage_list[cmdname] = usage
        except ValueError as e_fe:
            print "Module " + name + " has an error with the help() interface: " + str(e_fe)

    print usage_list
    return usage_list


modules = {}
module_import_list(["samba", "lastfm", "watch", "stats", "youtube", "weather"])

# Global variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.yellow
ircbacklog = list()
ircbacklog_in = list()
ircbacklog_out = list()
# TODO migrate it to the module_commands stuff
commandsavail = "awesome, nyaa, help, quit*, triggers, replay*, say, act, kick*, date, ddate, version"
telegram_cur_nick = None

# Variables declared by config file
cfg = Config()
maxbacklog = int(cfg.backlog())

# TODO instance will in the future be a list of all connections
instance = Client()

# Main()
if __name__ == "__main__":

    module_start()

    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    instance.connect()

    try:
        instance.eventloop()
    except Exception as e:
        module_shutdown()
        raise

    module_shutdown()
