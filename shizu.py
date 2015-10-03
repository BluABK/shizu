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
import socket           # A rather *useful* network tool
import time             # For time-based greeting functionality
import re               # Regex for the win.
import ConfigParser
from random import randint
# from subprocess import check_output
from subprocess import *
from collections import deque
import os
import unicodedata


# Project-specific modules
import colours as clr
clr_selection = deque([clr.green, clr.red, clr.blue, clr.purple, clr.cyan, clr.white])


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print "[shizu/import]:\t ERROR: Unable to import %s, expect issues!" % module_name
        return False
    else:
        return True

if module_exists("modules.samba") is True:
    import modules.samba as samba            # for server-side samba functionality
#    clr = clr_selection.popleft()
#    samba.my_colour = clr
#    clr_selection.append(clr)
if module_exists("modules.lastfm") is True:
    import modules.lastfm as lastfm
#    clr = clr_selection.popleft()
#    lastfm.my_colour = clr
#    clr_selection.append(clr)
if module_exists("modules.watch") is True:
    import modules.watch as watch
#    clr = clr_selection.popleft()
#    watch.my_colour = clr
#    clr_selection.append(clr)
if module_exists("modules.stats") is True:
    import modules.stats as stats
if module_exists("modules.youtube") is True:
    import modules.youtube as youtube
#    clr = clr_selection.popleft()
#    stats.my_colour = clr
#    clr_selection.append(clr)
if module_exists("weather"):
    import weather as yr

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
youtube_url = ""
yr_stations = []


class Config:  # Shizu's config class # TODO: Add ConfigParser for writing changes to config.ini
    default = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.default.read('config.ini')

    def server(self):
        return str(self.default.get('irc', 'server'))

    def spass(self):
        return str(self.default.get('irc', 'password'))

    def port(self):
        return int(self.default.get('irc', 'port'))

    def chan(self):
        return str(self.default.get('irc', 'channel'))

    def nick(self):
        return str(self.default.get('irc', 'nickname'))

    def realname(self):
        return str(self.default.get('irc', 'real name'))

    def cmdsym(self):
        return str(self.default.get('irc', 'cmdsymbol'))

    def quitmsg(self):
        return str(self.default.get('irc', 'quit-message'))

    def quitpro(self):
        return str(self.default.get('irc', 'quit-protection'))

    def proxy_nicks(self):
        # try:
        return_dbg = self.default.get('irc', 'proxy-users')
        return return_dbg
    #    except ConfigParser.NoSectionError:
    #        return "That section does not seem to exist"
    #    except ConfigParser.NoOptionError:
    #        return "Option does not seem to exist"

    def su(self):
        return str(self.default.get('users', 'superusers'))

    def nspass(self):
        return str(self.default.get('nickserv', 'password'))

    def backlog(self):
        return str(self.default.getint('irc', 'backlog-limit'))

    def triggers_words(self):
        return str(self.default.get('triggers', 'words'))

    def triggers_badwords(self):
        return str(self.default.get('triggers', 'badwords'))

    def triggers_ignorednicks(self):
        return str(self.default.get('triggers', 'ignored-nicks'))

    def commands_ignorednicks(self):
        return str(self.default.get('commands', 'ignored-nicks'))

    def chk_command_perms(self, user, inst):
        try:
            allowed = str(self.default.get('custom-cmd-cfg', inst))
            if user in allowed:
                return True
            else:
                return False
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    # TODO: May be static
    def add_command(self, name, function):
        try:
            config = Config.default
            config.set('custom-cmd', name, function)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    # TODO: May be static
    def add_rawcommand(self, name, function):
        try:
            config = Config.default
            config.set('custom-rawcmd', name, function)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    # TODO: May be static
    def del_command(self, name):
        try:
            config = Config.default
            config.remove_option('custom-cmd', name)
            with open('config.ini', 'w') as confgfile:
                config.write(confgfile)
            # return self.config.remove_option('custom-cmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    # TODO: May be static
    def del_rawcommand(self, name):
        try:
            config = Config.default
            config.remove_option('custom-rawcmd', name)
            with open('config.ini', 'w') as confgfile:
                config.write(confgfile)
            # return self.config.remove_option('custom-rawcmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def get_command(self, name):
        try:
            return str(self.default.get('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def get_rawcommand(self, name):
        try:
            return str(self.default.get('custom-rawcmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def chk_command(self, name):
        try:
            return str(self.default.has_option('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def chk_rawcommand(self, name):
        try:
            return str(self.default.has_option('custom-rawcmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def lst_command(self):
        try:
            return self.default.items('custom-cmd')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def lst_rawcommand(self):
        try:
            return self.default.items('custom-rawcmd')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"

    def lst_command_option(self):
        try:
            optlist = list()
            for item in self.default.items('custom-cmd'):
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
            for item in self.default.items('custom-rawcmd'):
                optlist.append(item[0])
            return optlist
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        # except:
        #    return "An unknown exception occurred"


# Variables declared by config file
cfg = Config()
maxbacklog = int(cfg.backlog())


def ian(s):  # is a number
    try:
        int(s)
        return True
    except ValueError:
        return False


def ping(ircsock):
    ircsock.send("PONG :Pong\n")


def sendmsg(msg, chan, ircsock):
    try:
        if isinstance(msg, basestring):
            try:
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, msg))
            except ValueError:
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Oi! That's not a string OwO Are you trying to kill me?!"))
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Hey... Are you trying to kill me?!"))
        else:
            # Don't check, errors from here are raised
            for item in msg:
                sendmsg(item, chan, ircsock)
    except TypeError:
        ircsock.send("PRIVMSG %s :A TypeError occurred, that's annoying..\r\n" % chan)


def debug(msg, ircsock):
    ircsock.send("PRIVMSG %s :DEBUG: %s\r\n" % (cfg.chan(), msg))


def join(chan, ircsock):
    ircsock.send("JOIN " + chan + "\n")


def getgreeting(greeter, ircsock):
    t = int(time.strftime("%H"))

    if t >= 17 or t < 4:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    elif t <= -1:
        debug("Negative time returned", ircsock)
        greeting = "ohi"
    else:
        debug("Time returned had no valid integer value.", ircsock)
        greeting = "ohi"

    return "%s %s~" % (greeting, greeter)


def replay(lines, chan, direction, ircsock):
    if direction == 0:
        to_send = ircbacklog[-lines:]
    elif direction == 1:
        to_send = ircbacklog_in[-lines:]
    elif direction == 2:
        to_send = ircbacklog_out[-lines:]
    else:
        to_send = ircbacklog[-lines:]
        sendmsg("DERP invalid direction! Defaulting to duplex", chan, ircsock)

    for m in to_send:
        sendmsg(m, chan, ircsock)


def ircquit(ircsock):
    watch.stop()
    sendraw("QUIT %s\r\n" % cfg.quitmsg(), ircsock)
    ircsock.close()


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
    return check_output("date", shell=True)


def ddate():
    return check_output("ddate", shell=False)


def whois(user, selection, raw_in, ircsock):
    global ircbacklog, ircbacklog_out
    sendraw("WHOIS %s\n" % user, ircsock)
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
def check_id(user, facility, raw_in, ircsock):
    # Check if user is identified with nickserv
    print("Checking ID...\n")
    if facility == "identified":
        # sendmsg("facility = id", chan)
        chk = whois(user, "identified", raw_in, ircsock)
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

    # sendmsg("DEBUG: %s" % check_everyone, chan)

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


def custom_command(name, chan, ircsock):
    sendmsg(cfg.get_command(name), chan, ircsock)


def custom_rawcommand(cmd, usernick, chan, ircsock):
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
        sendraw(c, ircsock)


def version():
    c_date = str(check_output("git show -s --format=%ci", shell=True)).strip("\n")
    c_hash_short = str(check_output("git rev-parse --short HEAD", shell=True)).strip("\n")

    retv = c_date + " (" + c_hash_short + ")"
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

    return [real_nick, msg]


def yr_init():
    yr.create_stations(yr.download(yr.station_loc_url, coding="", limit=0, debug=True))


def commands(usernick, msg, chan, ircsock):
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
        sendmsg("Everything is awesome!", chan, ircsock)
    elif cmd[0].lower() == "version":
        sendmsg("%s" % version(), chan, ircsock)
    elif cmd[0].lower() == "nyaa":
        sendmsg("Nyaa~", chan, ircsock)
    elif cmd[0].lower() == "date":
        sendmsg(date(), chan, ircsock)
    elif cmd[0].lower() == "ddate":
        sendmsg(ddate(), chan, ircsock)
    elif cmd[0].lower() == "dump":
        try:
            if cmd[1] == "cmd":
                if len(cmd) > 1:
                    if cmd[2] == "ignorednicks":
                        sendmsg("Ignored nicks: %s" % cfg.commands_ignorednicks(), chan, ircsock)
            elif cmd[1] == "trg":
                if len(cmd) > 1:
                    if cmd[2] == "ignorednicks":
                        try:
                            sendmsg("Ignored nicks: %s" % cfg.triggers_ignorednicks(), chan, ircsock)
                        except TypeError:
                            sendmsg("An error occurred, sue me", chan, ircsock)
            elif cmd[1] == "lastfm":
                if len(cmd) > 1:
                    if cmd[2] == "alias":
                        # try:
                        da_list = lastfm.cfg.list_alias()
                        # for i in range(len(da_list[0])):
                        #    for item in da_list:
                        #        print item[i]
                        # print da_list
                        sendmsg(da_list, chan, ircsock)
                        # except:
                        #    sendmsg("An error occurred, sue me", chan, ircsock)
            else:
                sendmsg("Available parameters for this debug function:"
                        " {cmd ignorednicks, trg ignorednicks, lastfm alias}", chan, ircsock)
        except IndexError:
            sendmsg("INFODUMP: Invalid argument(s)", chan, ircsock)
    elif cmd[0].lower() == "kick":

        # Make sure that it is an actual user
        if ignored_nick("commands", usernick) is True:
            sendmsg("%s: Abuse by proxy? Nice try... ಠ_ಠ" % usernick, chan, ircsock)
            return

        # Check if user is authorised to do so
        for u in cfg.su().lower().split(","):
            if usernick.lower() == u:
                try:
                    try:
                        # KICK <user> <reason>
                        sendraw("KICK %s %s %s\n" % (chan, cmd[1], cmd[2]), ircsock)
                        return
                    except IndexError:
                        # KICK <user> <static reason> (fallback if no reason given)
                        sendraw("KICK %s %s *shove*\n" % (chan, cmd[1]), ircsock)
                        return
                except IndexError:
                    print("IndexError in authorisation check")
                    return

        # If all else fails, user was probably not authorised and must be punished for abuse
        sendraw("KICK %s %s Backfired, oh the irony! ~\n" % (chan, usernick), ircsock)

    elif cmd[0].lower() == "replay":
        # TODO not 100% sure here, debug the backlog list a little and find out if this is safe
        if len(cmd) > 2 and ian(cmd[1]) and int(cmd[1]) <= maxbacklog:
            try:
                if cmd[2] == "duplex":
                    replay(int(cmd[1]), chan, 0, ircsock)
                elif cmd[2] == "recv":
                    replay(int(cmd[1]), chan, 1, ircsock)
                elif cmd[2] == "send":
                    replay(int(cmd[1]), chan, 2, ircsock)
            except IndexError:
                sendmsg("WHOA! IndexError in cmd[2] o_0", chan, ircsock)
                replay(int(cmd[1]), chan, 0, ircsock)
        else:
            replay(maxbacklog, chan, 0, ircsock)
    elif cmd[0].lower() == "say":
        if len(cmd) > 1:
            # Secure outgoing message
            if (re.match(r"^\x01[^\s]*", cmd[1]) is None) and (re.match(r"^![^\s]+", cmd[1]) is None):
                sendmsg(" ".join(cmd[1:]), chan, ircsock)
        else:
            sendmsg("Syntax: %ssay <string>" % cfg.cmdsym(), chan, ircsock)
    elif cmd[0].lower() == "act":
        sendmsg("\x01ACTION %s\x01" % " ".join(cmd[1:]), chan, ircsock)
    elif cmd[0].lower() == "join":
        # Ability to join multiple channels
        newchans = cmd[1:]
        for newchan in newchans:
            if newchan[0] == '#':
                ircsock.send("JOIN %s\r\n" % newchan)
            else:
                ircsock.send("JOIN #%s\r\n" % newchan)
    elif cmd[0].lower() == "quit" and usernick in cfg.su():  # and cmd[1] == cfg.quitpro():
            ircquit(ircsock)

    elif cmd[0].lower() == "host":
        if len(cmd) > 1:
            try:
                retval = check_output("host %s" % cmd[1], shell=True)
                # for line in retval:
                #   sendmsg(line, chan)
                sendmsg(retval, chan, ircsock)
            except CalledProcessError:
                sendmsg("Invalid argument.... (and you *know* it)", chan, ircsock)

    # Help calls
    if cmd[0].lower() == "help":
        try:
            if cmd[1] == "triggers":
                sendmsg("%s: Syntax: <trigger> %s" % (usernick, cfg.nick()), chan, ircsock)
                sendmsg("Available triggers: %s " % cfg.triggers_words(), chan, ircsock)
            elif cmd[1] == "replay":
                sendmsg("%s: Syntax: %sreplay <lines> <direction>" % (usernick, cfg.cmdsym()), chan, ircsock)
                sendmsg("Available commands: recv, send, duplex", chan, ircsock)
            elif cmd[1] == "kick":
                sendmsg("%s: Syntax: %skick <user>" % (usernick, cfg.cmdsym()), chan, ircsock)
            elif cmd[1] == "samba":
                if len(cmd) > 2:
                    if cmd[2] == "logins":
                        sendmsg("%s: Syntax: %ssamba logins <user>" % (usernick, cfg.cmdsym()), chan, ircsock)
                else:
                    for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                        sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan, ircsock)
            elif cmd[1] == "lastfm":
                if len(cmd) > 2:
                    if cmd[2] == "recent":
                        sendmsg("%s: Syntax: %slastfm recent <user> <num>" % (usernick, cfg.cmdsym()), chan, ircsock)
                else:
                    for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                        sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan, ircsock)
        except IndexError:
            helpcmd(usernick, chan, ircsock)

    # module lastfm
    elif cmd[0].lower() == "lastfm":
        if len(cmd) > 1:
            if cmd[1] == "bio":
                if len(cmd) > 2:
                    feedback = lastfm.artist_bio(cmd[2])
                    if isinstance(feedback, str):
                        sendmsg(str(feedback), chan, ircsock)
                    # elif isinstance(feedback, list):
                    else:
                        for i in feedback:
                            sendmsg(str(i), chan, ircsock)
            elif cmd[1] == "status":
                auth = lastfm.test_connection()
                print auth
                print type(auth)

                if type(auth) is Exception:
                    sendmsg(str(auth.message), chan, ircsock)
                    sendmsg(str(auth.details), chan, ircsock)
                else:
                    auth = unicodedata.normalize('NFKD', auth).encode('ascii', 'ignore')
                    print auth
                    print type(auth)
                    net = lastfm.network.name
                    print net
                    print type(net)

                    # if type(auth) is str and type(net) is str:
                    if type(auth) is str and type(net) is str:
                        sendmsg("I am currently authenticated as " + auth + " on " + net, chan, ircsock)
                    elif type(auth) is str:
                        sendmsg("I am currently authenticated as " + auth + " on *NO NETWORK*, how does that even work? =/",
                                chan, ircsock)
                    elif net is str:
                        sendmsg("I am somehow connected to " + net + ", but not authenticated... Okay then!", chan, ircsock)
                    else:
                        sendmsg("I am unable to query the network, is LastFM throwing a fit?", chan, ircsock)
            elif cmd[1] == "set":
                if len(cmd) > 2:
                    if cmd[2] == "alias":
                        if len(cmd) > 3:
                            tmp = lastfm.add_alias(usernick, cmd[3])
                            sendmsg(tmp, chan, ircsock)

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
                    sendmsg(test, chan, ircsock)
                elif test is None:
                    sendmsg("%s has not played anything in the given period" % nick, chan, ircsock)
                elif test == "None":
                    sendmsg("%s: No user named '%s' was found =/" % (nick, test), chan, ircsock)
                else:
                    sendmsg("%s has recently played:" % nick, chan, ircsock)
                    for item in xrange(len(test)):
                        sendmsg(str(test[item]), chan, ircsock)
            # Print help
            else:
                for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                    sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan, ircsock)

    elif cmd[0].lower() == "ragequit":
        raise Exception("spam", "eggs")

    # Module: lastfm - shortcuts
    elif cmd[0].lower() == "np":
        try:
            test = lastfm.now_playing(cmd[1])
            if test is None:
                sendmsg("%s is not currently playing anything" % cmd[1], chan, ircsock)
            elif test == "None":
                sendmsg("No user named '%s' was found =/" % cmd[1], chan, ircsock)
            elif test == "timeout":
                sendmsg("Request timed out =/", chan, ircsock)
            else:
                sendmsg("%s is currently playing: %s" % (cmd[1], test), chan, ircsock)
        except IndexError:
            test = lastfm.now_playing(usernick)
            if test is None:
                sendmsg("%s is not currently playing anything" % usernick, chan, ircsock)
            elif test == "None":
                sendmsg("%s: No user named '%s' was found =/ "
                        "You can set an alias with !lastfm set alias <lastfmuser>" % (usernick, test), chan, ircsock)
            elif test == "timeout":
                sendmsg("Request timed out =/", chan, ircsock)
            else:
                sendmsg("%s is currently playing: %s" % (usernick, test), chan, ircsock)

    elif cmd[0].lower() == "npt":
        try:
            sendmsg("%s is currently playing; %s" % (usernick, lastfm.test_playing(cmd[1])), chan, ircsock)
        except IndexError:
            sendmsg("Index derp", chan, ircsock)

    # Module: samba
    elif cmd[0].lower() == "samba":
        if len(cmd) > 1:
            if cmd[1] == "logins":
                sendmsg(samba.get_logins(cmd[2:]), chan, ircsock)
            elif cmd[1] == "np":
                if usernick.lower() == "bluabk":
                    sendmsg(samba.get_playing(), chan, ircsock)
                else:
                    sendmsg("%s: Get your own damn service, leech!" % usernick, chan, ircsock)
            elif cmd[1] == "np2":
                if usernick.lower() == "bluabk":
                    sendmsg(samba.get_playing2(), chan, ircsock)
                else:
                    sendmsg("%s: Get your own damn service, leech!" % usernick, chan, ircsock)
        else:
            for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan, ircsock)

    # Debug commands
    elif cmd[0].lower() == "debug":
        if len(cmd) >= 2 and cmd[1] == "logins":
            dbg = samba.get_logins(cmd[2:])
            debug("Passed variable of length:" + str(len(dbg)), ircsock)
            for itr in range(len(dbg)):
                debug("Iteration: %s/%s" % (str(itr), str(len(dbg))), ircsock)
                debug(dbg[itr], ircsock)

    # Custom commands
    elif cmd[0].lower() == "addcommand":
        if ignored_nick("commands", usernick) is True:
            sendmsg("%s:ಠ_ಠ" % usernick, chan, ircsock)
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
            sendmsg(ret, chan, ircsock)

    elif cmd[0].lower() == "removecommand":
        if ignored_nick("commands", usernick) is True:
            sendmsg("%s:ಠ_ಠ" % usernick, chan, ircsock)
            return
        if len(cmd) > 1:
            ret = del_custom_cmd(str(cmd[1]), usernick)
            sendmsg(ret, chan, ircsock)

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
            sendmsg(ret, chan, ircsock)

    elif cmd[0].lower() == "removerawcommand" and usernick.lower() == "bluabk":
        if len(cmd) > 1:
            ret = del_custom_rawcmd(str(cmd[1]), usernick)
            sendmsg(ret, chan, ircsock)

    elif cmd[0].lower() == "listcustom":
        string_list = ""
        for item in cfg.lst_command():
            string_list += (item[0] + " ")
        for item in cfg.lst_rawcommand():
            string_list += (item[0] + "* ")
        sendmsg(string_list, chan, ircsock)

    # Module: Watch
    elif cmd[0].lower() == "watch":
        if len(cmd) > 1:
            if cmd[1] == "enable":
                watch_enabled = True
                sendmsg("Watch notifications enabled.", chan, ircsock)

            elif cmd[1] == "disable":
                watch_enabled = False
                sendmsg("Watch notifications disabled.", chan, ircsock)

            elif cmd[1] == "limit":
                print "watch: Setting watchlimit to %s" % cmd[2]
                watch.set_notify_limit(cmd[2])
                sendmsg("Watch notifications limit set to %s" % cmd[2], chan, ircsock)
        else:
            for item in xrange(len(watch.helpcmd(cfg.cmdsym()))):
                sendmsg(str(watch.helpcmd(cfg.cmdsym())[item]), chan, ircsock)

    # Module: Stats
    elif cmd[0].lower() == "stats":
        if len(cmd) > 1:
            if cmd[1] == "cmd" or cmd[1] == "command":
                if len(cmd) > 2:
                    sendmsg(stats.get_cmd(cmd[2]), chan, ircsock)
                else:
                    for item in stats.get_cmd_all():
                        sendmsg("%s = %s" % (item[0], item[1]), chan, ircsock)

            elif cmd[1] == "user":
                # TODO: Code user stats get command
                sendmsg("Dummy function", chan, ircsock)
        else:
            for item in xrange(len(stats.helpcmd(cfg.cmdsym()))):
                sendmsg(str(stats.helpcmd(cfg.cmdsym())[item]), chan, ircsock)

    elif cmd[0].lower() in cfg.lst_command_option():
        print "Executing custom command"
        custom_command(cmd[0].lower(), chan, ircsock)

    elif cmd[0].lower() in cfg.lst_rawcommand_option() and usernick in cfg.su():
        print "Executing custom rawcommand"
        custom_rawcommand(cmd, usernick, chan, ircsock)

    # Module: YouTube
    elif cmd[0].lower() == "ytt" and module_exists("modules.youtube"):
        global youtube_url
        if youtube_url != "":
            sendmsg(youtube.get_title(youtube_url), chan, ircsock)
            youtube_url = ""

    # Private Module: yr
    elif cmd[0].lower() == "yr" and module_exists("weather"):
        if len(cmd) > 1:
            #try:
            yr.init()
            forecast = yr.weather_update(" ".join(map(str, cmd[1:])), debug=True)
            sendmsg(forecast, chan, ircsock)
            #except:
            #    sendmsg("https://www.konata.us/nope.gif", chan, ircsock)


def triggers(usernick, msg, chan, ircsock):
    greet_pat = re.compile((cfg.triggers_words() + " "), flags=re.IGNORECASE)
    greet_match = re.match(greet_pat, msg)
    nick_match = False
# TODO: HACK: Actually regex match against msg having exactly triggers_words() + cfg.nick()
    for s in msg.split(" "):
        if s == cfg.nick():
            nick_match = True

    try:
        # if matches.group(0) != "":  # If someone greets me, I will greet back.
        if greet_match and nick_match:
            sendmsg((getgreeting(usernick, ircsock)), chan, ircsock)
    except AttributeError:
        return


def listeners(usernick, msg, chan, ircsock):
    if module_exists("modules.youtube"):
        global youtube_url
        #if re.search(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', msg).group(0):
        for item in msg.split():
            if re.search('(http[s]?://)?(www.)?(youtube.com|youtu.?be)/+', item):
                print "YouTube: current = %s" % item
                youtube_url = item


def watch_notify(files, chan, msg, ircsock):
    for item in files:
        sendmsg("%s %s" % (msg, item), chan, ircsock)


def watch_notify_moved(files, chan, ircsock):
    # index = 0
    # strings = list()
    # for li in files:
    # for index in xrange(li[0]):

    # lame ass hack
    for item in files:
        sendmsg(item, chan, ircsock)


def helpcmd(user, chan, ircsock):
    sendmsg("%s: Syntax: %scommand help arg1..argN" % (user, cfg.cmdsym()), chan, ircsock)
    sendmsg("Available commands: %s, %s (* command contains sub-commands)" %
            (commandsavail, modulesavail), chan, ircsock)


# ircsock send relay
def sendraw(buf, ircsock):
    global ircbacklog, ircbacklog_out

    sent = ircsock.sendall(buf)

    ircbacklog.append(sent)
    if len(ircbacklog) > maxbacklog:
            # Delete first entry
            ircbacklog = ircbacklog[1:]

    ircbacklog_in.append(sent)
    if len(ircbacklog_out) > maxbacklog:
            # Delete first entry
            ircbacklog_out = ircbacklog_out[1:]


class Client:

    def __init__(self):
        print "Spawned client instance"

    # Connect to the the server
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((cfg.server(), cfg.port()))
    # Send password before registration [RFC2812 section-3.1.1 Password message]
    if cfg.spass() != "":
        sendraw("PASS " + cfg.spass() + "\n", ircsock)
    # Register with the server [RFC2812 section-3.1 Connection Registration]
    sendraw("NICK " + cfg.nick() + "\n", ircsock)
    sendraw("USER %s %s %s :%s\n" % (cfg.nick(), "0", "*", cfg.realname()), ircsock)

    i = 1

    for recvraw in ircsock.makefile():
        if not running:
            break

        if recvraw == '':
            continue

        ircbacklog.append(recvraw)

        if len(ircbacklog) > maxbacklog:
            # Delete first entry
            ircbacklog = ircbacklog[1:]

        ircbacklog_in.append(recvraw)

        if len(ircbacklog_in) > maxbacklog:
            # Delete first entry
            ircbacklog_in = ircbacklog_in[1:]

        ircmsg = recvraw.strip("\n\r")          # Remove protocol junk (linebreaks and return carriage)
        ircmsg = ircmsg.lstrip(":")             # Remove first colon. Useless, waste of space >_<
        print("%s: %s" % (i, ircmsg))           # Print received data

        ircparts = re.split("\s", ircmsg, 3)

        if ircparts[0] == '':
            continue

        if recvraw.find("433 * %s :Nickname is already in use." % cfg.nick()) != -1:
            sendraw("NICK " + (cfg.nick() + "|" + str(randint(0, 256))) + "\n", ircsock)

        if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
            ping(ircsock)

        if ircmsg.find("NOTICE %s :This nickname is registered" % cfg.nick()) != -1:
            sendraw("PRIVMSG NickServ :identify %s\r\n" % cfg.nspass(), ircsock)

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(cfg.chan(), ircsock)

        # Run some checks

        # Rejoin on kick
        # TODO: Make optional and abbreviate into methods
        if ircmsg.find("KICK #") != -1:
            # TODO: HACK: Rejoin all channels
            join(cfg.chan(), ircsock)
        #    for num in channel:
        #        print "DEBUG: %s" % num
        #        if ircmsg.find("KICK %s" % channel[num]):
        #            join(channel[num])
        #    sendmsg("Oi, That was mean! T_T")
        #    sendmsg("Oi, That was mean! T_T", channel[num])

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

            commands(tmpusernick, message, channel, ircsock)
            triggers(tmpusernick, message, channel, ircsock)
            listeners(tmpusernick, message, channel, ircsock)

            if watch.check_added():
                if watch_enabled:
                    if len(watch.get_added()) <= watch.notify_limit():
                        watch_notify(watch.get_added(), watch.notify_chan(), watch.cfg.msg_add(), ircsock)
                        for test in watch.get_added():
                            print ("\033[94mNotified: %s\033[0m" % test)
                    else:
                        cap_list = list()
                        for item in watch.get_added()[0:(watch.notify_limit())]:
                            cap_list.append(item)

                        cap_list[watch.notify_limit()-1] += \
                            " ... and " + str(len(watch.get_added()) - watch.notify_limit()) + " more unlisted entries"
                        watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_add(), ircsock)
                else:
                    for test in watch.get_added():
                        print ("\033[94mIgnored notify: %s\033[0m" % test)

                watch.clear_added()

            if watch.check_erased():
                if watch_enabled:
                    if len(watch.get_erased()) <= watch.notify_limit():
                        watch_notify(watch.get_erased(), watch.notify_chan(), watch.cfg.msg_del(), ircsock)
                        print "Debug del sign is %s" % watch.cfg.msg_del()
                        for test in watch.get_erased():
                            print ("\033[94mNotified: %s\033[0m" % test)
                    else:
                        cap_list = list()
                        for item in watch.get_erased()[0:(watch.notify_limit())]:
                            cap_list.append(item)

                        cap_list[watch.notify_limit()-1] += \
                            " ... and " + str(len(watch.get_erased()) - watch.notify_limit()) + " more unlisted entries"
                        print "Debug2 del sign is %s" % watch.cfg.msg_del()
                        watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_del(), ircsock)
                else:
                    for test in watch.get_erased():
                        print ("\033[94mIgnored notify: %s\033[0m" % test)

                watch.clear_erased()

            if watch.check_moved():
                if watch_enabled:
                    if len(watch.get_moved()) <= watch.notify_limit():
                        watch_notify_moved(watch.get_moved(), watch.notify_chan(), ircsock)
                        for test in watch.get_moved():
                            print ("\033[94mNotified: %s\033[0m" % test)
                    else:
                        cap_list = list()
                        for item in watch.get_moved()[0:(watch.notify_limit())]:
                            cap_list.append(item)

                        cap_list[watch.notify_limit()-1] += \
                            " ... and " + str(len(watch.get_moved()) - watch.notify_limit()) + " more unlisted entries"
                        watch_notify(cap_list, watch.notify_chan(), watch.cfg.msg_mov(), ircsock)
                # else:
                #    for test in watch.get_moved():
                #        print ("\033[94mIgnored notify: %s\033[0m" % test)

                watch.clear_moved()

        # And the tick goes on...
        i += 1

    # See ya!
    ircquit(ircsock)

# Main()
if __name__ == "__main__":
    try:
        instance = Client()
    except Exception as e:
        watch.notifier.stop()
        raise

