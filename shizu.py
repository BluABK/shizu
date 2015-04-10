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
from subprocess import check_output

# Project-specific modules
import modules.samba as samba            # for server-side samba functionality
import modules.lastfm as lastfm
#import db               # for server-side file search and lookup

# Global variables

ircbacklog = list()
ircbacklog_in = list()
ircbacklog_out = list()
running = True
commandsavail = "awesome, nyaa, help, quit*, triggers, replay*, say, act, kick*, date, ddate"
modulesavail = "samba*"


class Config:  # Shizu's config class # TODO: Add ConfigParser for writing changes to config.ini
    config = ConfigParser.RawConfigParser()

    def __init__(self):
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

    def cmdsym(self):
        return str(self.config.get('irc', 'cmdsymbol'))

    def quitmsg(self):
        return str(self.config.get('irc', 'quit-message'))

    def quitpro(self):
        return str(self.config.get('irc', 'quit-protection'))

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

    def add_command(self, name, function):
        try:
            self.config.set('custom-cmd', name, function)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def del_command(self, name):
        try:
            return self.config.remove_option('custom-cmd', name)
        except ConfigParser.NoSectionError:
            return "That section does not seem to exist"

    def get_command(self, name):
        try:
            return str(self.config.get('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        except:
            return "An unknown exception occured"

    def chk_command(self, name):
        try:
            return str(self.config.has_option('custom-cmd', name))
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        except:
            return "An unknown exception occured"

    def lst_command(self):
        try:
            return self.config.items('custom-cmd')
        except ConfigParser.NoSectionError:
            return "That section does not seem to exis"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        except:
            return "An unknown exception occured"

    def lst_command_option(self):
        try:
            optlist = list()
            for item in self.config.items('custom-cmd'):
                optlist.append(item[0])
            return optlist
        except ConfigParser.NoSectionError:
            return "That section does not seem to exis"
        except ConfigParser.NoOptionError:
            return "Option does not seem to exist"
        except:
            return "An unknown exception occured"


# Variables declared by config file
cfg = Config()
maxbacklog = int(cfg.backlog())


def ian(s):  # is a number
    try:
        int(s)
        return True
    except ValueError:
        return False


def ping():
    ircsock.send("PONG :Pong\n")


def sendmsg(msg, chan):
    if isinstance(msg, basestring):
        try:
            ircsock.send("PRIVMSG %s :%s\r\n" % (chan, msg))
        except ValueError:
            ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Oi! That's not a string OwO Are you trying to kill me?!"))
            ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Hey... Are you trying to kill me?!"))
    else:
        # Don't check, errors from here are raised
        for item in msg:
            sendmsg(item, chan)


def debug(msg):
    ircsock.send("PRIVMSG %s :DEBUG: %s\r\n" % (cfg.chan(), msg))


def join(chan):
    ircsock.send("JOIN " + chan + "\n")


def getgreeting(greeter):
    t = int(time.strftime("%H"))

    if t >= 17 or t < 4:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    elif t <= -1:
        debug("Negative time returned")
        greeting = "ohi"
    else:
        debug("Time returned had no valid integer value.")
        greeting = "ohi"

    return "%s %s~" % (greeting, greeter)


def replay(lines, chan, direction):
    if direction == 0:
        tosend = ircbacklog[-lines:]
    elif direction == 1:
        tosend = ircbacklog_in[-lines:]
    elif direction == 2:
        tosend = ircbacklog_out[-lines:]
    else:
        tosend = ircbacklog[-lines:]
        sendmsg("DERP invalid direction! Defaulting to duplex", chan)

    for m in tosend:
        sendmsg(m, chan)


def ircquit():
    global running  # TODO: Figure out why this lone global refuse to be defined with the rest at the top
    running = False


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


def whois(user, selection, raw_in):
    global ircbacklog, ircbacklog_out
    sendraw("WHOIS %s\n" % user)
    data = list()

    prevmsg = ""
    msgcount = 0
    for n in xrange(len(ircbacklog)):
        #nyaa = str(ircbacklog[n])
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
def check_id(user, facility, raw_in):
    # Check if user is identified with nickserv
    print("Checking ID...\n")
    if facility == "identified":
#        sendmsg("facility = id", chan)
        chk = whois(user, "identified", raw_in)
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
    if usernick in cfg.su():
        print str(function)
        print "Adding custom command: %s with function %s, requested by %s" % (name, function, usernick)
        print cfg.chk_command(name)
        #if name not in commandsavail and cfg.chk_command(name) is False:
        collision = False
        if name in commandsavail:
            collision = True

        print "collision is %s" % collision
        #if collision is False and cfg.chk_command(name) is False:
        if collision is True:
            return "That name collides with something =/"
        elif cfg.chk_command(name) is True:
            return "That name collides with something =/"
        else:
            test = cfg.add_command(name, function)
            if isinstance(test, str):
                return test
            else:
                return "Command %s added successfully! ^_^" % name


def del_custom_cmd(name, usernick):
    if usernick in cfg.su() and cfg.chk_command(name) is True:
        cfg.del_command(name)
        return "Command removed"
    else:
        return "Unable to remove given command"


def custom_command(name, chan):
    sendmsg(cfg.get_command(name), chan)


def commands(usernick, msg, raw_in, chan):
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
    if usernick != "HoloBot":			# TODO: make nick-exclusions in config.ini
        # General commands
        if cmd[0] == "awesome":
            sendmsg("Everything is awesome!", chan)
        elif cmd[0] == "nyaa":
            sendmsg("Nyaa~", chan)
        elif cmd[0] == "date":
            sendmsg(date(), chan)
        elif cmd[0] == "ddate":
            sendmsg(ddate(), chan)
        elif cmd[0] == "dump":
            try:
                if cmd[1] == "cmd":
                    if cmd[2] == "ignorednicks":
                        sendmsg("Ignored nicks: %s" % cfg.commands_ignorednicks(), chan)
                elif cmd[1] == "trg":
                    if cmd[2] == "ignorednicks":
                        sendmsg(("Ignored nicks: %s" % cfg.triggers_ignorednicks(), chan))
            except IndexError:
                sendmsg("INFODUMP: Invalid argument(s)", chan)
        elif cmd[0] == "kick":

            # Make sure that it is an actual user
            if ignored_nick("commands", usernick) is True:
                sendmsg("%s: Abuse by proxy? Nice try... ಠ_ಠ" % usernick, chan)
                return

            # Check if user is authorised to do so
            for u in cfg.su().lower().split(","):
                if usernick.lower() == u:
                    try:
                        try:
                            # KICK <user> <reason>
                            sendraw("KICK %s %s %s\n" % (chan, cmd[1], cmd[2]))
                            return
                        except IndexError:
                            # KICK <user> <static reason> (fallback if no reason given)
                            sendraw("KICK %s %s *shove*\n" % (chan, cmd[1]))
                            return
                    except IndexError:
                        print("IndexError in authorisation check")
                        return

            # If all else fails, user was probably not authorised and must be punished for abuse
            sendraw("KICK %s %s Backfired, oh the irony! ~\n" % (chan, usernick))

        elif cmd[0] == "replay":
            # TODO not 100% sure here, debug the backlog list a little and find out if this is safe
            if len(cmd) > 2 and ian(cmd[1]) and int(cmd[1]) <= maxbacklog:
                try:
                    if cmd[2] == "duplex":
                        replay(int(cmd[1]), chan, 0)
                    elif cmd[2] == "recv":
                        replay(int(cmd[1]), chan, 1)
                    elif cmd[2] == "send":
                        replay(int(cmd[1]), chan, 2)
                except IndexError:
                    sendmsg("WHOA! IndexError in cmd[2] o_0", chan)
                    replay(int(cmd[1]), chan, 0)
            else:
                replay(maxbacklog, chan, 0)
        elif cmd[0] == "say":
            # Secure outgoing message
            if (re.match(r"^\x01[^\s]*", cmd[1]) is None) and (re.match(r"^![^\s]+", cmd[1]) is None):
                sendmsg(" ".join(cmd[1:]), chan)
        elif cmd[0] == "act":
            sendmsg("\x01ACTION %s\x01" % " ".join(cmd[1:]), chan)
        elif cmd[0] == "join":
            # Ability to join multiple channels
            newchans = cmd[1:]
            for newchan in newchans:
                if newchan[0] == '#':
                    ircsock.send("JOIN %s\r\n" % newchan)
                else:
                    ircsock.send("JOIN #%s\r\n" % newchan)
        elif cmd[0] == "quit" and usernick in cfg.su(): #and cmd[1] == cfg.quitpro():
                ircquit()

        elif cmd[0] == "host":
            if len(cmd) > 1:
                retval = check_output("host %s" % cmd[1], shell=True)
                for line in retval:
                    sendmsg(line, chan)

        # Help calls
        if cmd[0] == "help":
            try:
                if cmd[1] == "triggers":
                    sendmsg("%s: Syntax: <trigger> %s" % (usernick, cfg.nick()), chan)
                    sendmsg("Available triggers: %s " % cfg.triggers_words(), chan)
                elif cmd[1] == "replay":
                    sendmsg("%s: Syntax: %sreplay <lines> <direction>" % (usernick, cfg.cmdsym()), chan)
                    sendmsg("Available commands: recv, send, duplex", chan)
                elif cmd[1] == "kick":
                    sendmsg("%s: Syntax: %skick <user>" % (usernick, cfg.cmdsym()), chan)
                elif cmd[1] == "samba":
                    if len(cmd) > 2:
                        if cmd[2] == "logins":
                            sendmsg("%s: Syntax: %ssamba logins <user>" % (usernick, cfg.cmdsym()), chan)
                    else:
                        for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                            sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan)
                elif cmd[1] == "lastfm":
                    if len(cmd) > 2:
                        if cmd[2] == "recent":
                            sendmsg("%s: Syntax: %slastfm recent <user> <num>" % (usernick, cfg.cmdsym()), chan)
                    else:
                        for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                            sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan)
            except IndexError:
                helpcmd(usernick, chan)

        # module lastfm
        elif cmd[0] == "lastfm":
            if len(cmd) > 1:
                if cmd[1] == "bio":
                    if len(cmd) > 2:
                        sendmsg(str(lastfm.artist_bio(cmd[2])), chan)
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
                    if test == "No user with that name was found":
                        sendmsg("%s: %s =/" % (test, nick), chan)
                    elif test == "None":
                        sendmsg("%s has not played anything in the given period" % nick, chan)
                    else:
                        sendmsg("%s has recently played:" % nick, chan)
                        for item in xrange(len(test)):
                            sendmsg(str(test[item]), chan)
            # Print help
            else:
                for item in xrange(len(lastfm.helpcmd(cfg.cmdsym()))):
                    sendmsg(str(lastfm.helpcmd(cfg.cmdsym())[item]), chan)

        # Module: lastfm - shortcuts
        elif cmd[0] == "np":
            try:
                test = lastfm.now_playing(cmd[1])
                if test == "No user with that name was found":
                    sendmsg("%s: %s =/" % (test, cmd[1]), chan)
                elif test == "None":
                    sendmsg("%s is not currently playing anything" % cmd[1], chan)
                else:
                    sendmsg("%s is currently playing: %s" % (cmd[1], test), chan)
            except IndexError:
                test = lastfm.now_playing(usernick)
                if test == "No user with that name was found":
                    sendmsg("%s: %s you can set an alias with !lastfm set alias <lastfmuser>" % (usernick, test), chan)
                elif test == "None":
                    sendmsg("%s is not currently playing anything" % usernick, chan)
                else:
                    sendmsg("%s is currently playing: %s" % (usernick, test), chan)

        elif cmd[0] == "npt":
            try:
                sendmsg("%s is currently playing; %s" % (usernick, lastfm.test_playing(cmd[1])), chan)
            except IndexError:
                sendmsg("Index derp", chan)

        # Module: samba
        elif cmd[0] == "samba":
            if len(cmd) > 1:
                if cmd[1] == "logins":
                    sendmsg(samba.getlogins(cmd[2:]), chan)
            else:
                for item in xrange(len(samba.helpcmd(cfg.cmdsym()))):
                    sendmsg(str(samba.helpcmd(cfg.cmdsym())[item]), chan)

        # Debug commands
        elif cmd[0] == "debug":
            if len(cmd) >= 2 and cmd[1] == "logins":
                dbg = samba.getlogins(cmd[2:])
                debug("Passed variable of length:" + str(len(dbg)))
                for itr in range(len(dbg)):
                    debug("Iteration: %s/%s" % (str(itr), str(len(dbg))))
                    debug(dbg[itr])

        # Custom commands
        elif cmd[0] == "addcommand":
            if len(cmd) > 1:
                arg = list()
                for item in xrange(len(cmd)):
                    if item > 1:
                        if item != "\n":
                            arg.append(cmd[item])
                            print "arg = %s" % arg
                fstr = " ".join(str(x) for x in arg)
                ret = add_custom_cmd(str(cmd[1]), fstr, usernick)
                sendmsg(ret, chan)

        elif cmd[0] == "removecommand":
            if len(cmd) > 1:
                ret = del_custom_cmd(str(cmd[1]), usernick)
                sendmsg(ret, chan)

        elif cmd[0] == "listcustom":
            string_list = ""
            for item in cfg.lst_command():
                string_list += (item[0] + " ")
            sendmsg(string_list, chan)

        elif cmd[0] in cfg.lst_command_option():
            custom_command(cmd[0], chan)


def triggers(usernick, msg, chan):
    greet_pat = re.compile((cfg.triggers_words() + " "), flags=re.IGNORECASE)
    greet_match = re.match(greet_pat, msg)
    nick_match = False
# TODO: HACK: Actually regex match against msg having exactly triggers_words() + cfg.nick()
    for s in msg.split(" "):
        if s == cfg.nick():
            nick_match = True

    try:
        #if matches.group(0) != "":  # If someone greets me, I will greet back.
        if greet_match and nick_match:
            sendmsg((getgreeting(usernick)), chan)
    except AttributeError:
        return


def helpcmd(user, chan):
    sendmsg("%s: Syntax: %scommand help arg1..argN" % (user, cfg.cmdsym()), chan)
    sendmsg("Available commands: %s, %s (* command contains sub-commands)" % (commandsavail, modulesavail), chan)


# ircsock send relay
def sendraw(buf):
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

# Main()
if __name__ == "__main__":
    # Connect to the the server
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((cfg.server(), cfg.port()))
    # Send password before registration [RFC2812 section-3.1.1 Password message]
    if cfg.spass() != "":
        sendraw("PASS " + cfg.spass() + "\n")
    # Register with the server [RFC2812 section-3.1 Connection Registration]
    sendraw("NICK " + cfg.nick() + "\n")
    sendraw("USER %s %s %s :%s\n" % (cfg.nick(), "0", "*", cfg.realname()))

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
            sendraw("NICK " + (cfg.nick() + "|" + str(randint(0, 256))) + "\n")

        if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
            ping()

        if ircmsg.find("NOTICE %s :This nickname is registered" % cfg.nick()) != -1:
            sendraw("PRIVMSG NickServ :identify %s\r\n" % cfg.nspass())

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(cfg.chan())

        # Run some checks

        # Rejoin on kick
        # TODO: Make optional and abbreviate into methods
        if ircmsg.find("KICK #") != -1:
        # TODO: HACK: Rejoin all channels
            join(cfg.chan())
        #    for num in channel:
        #        print "DEBUG: %s" % num
        #        if ircmsg.find("KICK %s" % channel[num]):
        #            join(channel[num])
        #    sendmsg("Oi, That was mean! T_T")
        #    sendmsg("Oi, That was mean! T_T", channel[num])

        if ircparts[1] != '' and ircparts[1] == "PRIVMSG":
            tmpusernick = ircparts[0].split('!')[0]
            channel = ircparts[2]
            if channel[0] != '#':
                channel = tmpusernick
            message = ircparts[3].lstrip(":")

            commands(tmpusernick, message, recvraw, channel)
            triggers(tmpusernick, message, channel)

        i += 1

    # See ya!
    sendraw("QUIT %s\r\n" % cfg.quitmsg())
    ircsock.close()
