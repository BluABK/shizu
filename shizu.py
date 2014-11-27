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

# Project-specific modules
import modules.samba as samba            # for server-side samba functionality
#import db               # for server-side file search and lookup

# Global variables
#global re # TODO: redeclared
global ircbacklog
global running

ircbacklog = list()
running = True
commandsavail = "awesome, nyaa, help, quit [protection], triggers, replay*, punishtec, say, act"
modulesavail = "samba*"
triggersavail = "Hello|O?hi|Ohay|Hey|Hiya|Heya|Ohayou|g\'day"

# Shortcut: Classes


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

    def nspass(self):
        return str(self.config.get('nickserv', 'password'))

    def backlog(self):
        return str(self.config.getint('irc', 'backlog-limit'))

# Shortcut: Variables declared by config file
cfg = Config()
maxbacklog = int(cfg.backlog())

# Shortcut: Functions


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

    return "%s %s~" % (greeting,  greeter)


def replay(lines, chan):
    tosend = ircbacklog[-lines:]
    for m in tosend:
        sendmsg(m, chan)


def ircquit():
    global running  # TODO: Figure out why this lone global refuse to be defined with the rest at the top
    running = False


def commands(usernick, msg, chan):
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
    if usernick != "SpyBot":			# TODO: make nick-exclusions in config.ini
        # General commands
        if cmd[0] == "awesome":
            sendmsg("Everything is awesome!", chan)
        elif cmd[0] == "nyaa":
            sendmsg("Nyaa~", chan)
        # Mess with the best, die like the rest ~
        elif cmd[0] == "punishtec":
            ircsock.send("KICK #blu SpyBot Mess with the best, die like the rest ~\r\n");
        elif cmd[0] == "replay":
            # TODO not 100% sure here, debug the backlog list a little and find out if this is safe
            if len(cmd) > 1 and ian(cmd[1]) and int(cmd[1]) <= maxbacklog:
                replay(int(cmd[1]), chan)
            else:
                replay(maxbacklog, chan)
        elif cmd[0] == "say":
            # join: " ".join(('say', 'a', 'b', 'c')[1:]) -> " ".join('a', 'b', 'c') => 'a b c'
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
        elif cmd[0] == "quit" and cmd[1] == cfg.quitpro():
                ircquit()

        # Help calls
        if cmd[0] == "help":
            try:
                if cmd[1] == "triggers":
                    sendmsg("%s: Syntax: <trigger> %s" % usernick, cfg.nick(), chan)
                    sendmsg("%s: Available triggers: %s " % usernick, triggersavail, chan)

                # Module: samba
                elif cmd[1] == "samba":
                # Split and don't die

                    if len(cmd) < 2 or cmd[1] == "help":
                        for item in xrange(len(samba.helpcmd())):
                            sendmsg(str(samba.helpcmd()[item]), chan)
                    elif cmd[2] == "logins":
                        sendmsg(samba.getlogins(cmd[2:]), chan)
            except IndexError:
                helpcmd(usernick, chan)

        # Debug commands
        if cmd[0] == "debug":
            if len(cmd) >= 2 and cmd[1] == "logins":
                dbg = samba.getlogins(cmd[2:])
                debug("Passed variable of length:" + str(len(dbg)))
                for itr in range(len(dbg)):
                    debug("Iteration: %s/%s" % (str(itr), str(len(dbg))))
                    debug(dbg[itr])


def triggers(usernick, msg, chan):
    matches = re.match("(Hello|O?hi|Ohay|Hey|Hiya|Heya|Ohayou|g\'day) " + cfg.nick(), msg, flags=re.IGNORECASE) # TODO: make it use triggers var
    try:
        if matches.group(0) != "":  # If someone greets me, I will greet back.
            sendmsg((getgreeting(usernick)), chan)
    except AttributeError:
        return


def helpcmd(user, chan):
    sendmsg("%s: Syntax: %scommand help arg1..argN" % (user, cfg.cmdsym()), chan)
    sendmsg("Available commands: %s, %s (* command contains sub-commands)" % (commandsavail, modulesavail), chan)

# Shortcut: Main()
if __name__ == "__main__":
    # Connect to the the server
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((cfg.server(), cfg.port()))
    # Send password before registration [RFC2812 section-3.1.1 Password message]
    if cfg.spass() != "":
        ircsock.send("PASS " + cfg.spass() + "\n")
    # Register with the server [RFC2812 section-3.1 Connection Registration]
    ircsock.send("NICK " + cfg.nick() + "\n")
    ircsock.send("USER %s %s %s :%s\n" % (cfg.nick(), "0", "*", cfg.realname()))

    i = 1

    for ircraw in ircsock.makefile():
        if not running:
            break

        if ircraw == '':
            continue

        ircbacklog.append(ircraw)

        if len(ircbacklog) > maxbacklog:
            # Delete first entry
            ircbacklog = ircbacklog[1:]

        ircmsg = ircraw.strip("\n\r")           # Remove protocol junk (linebreaks and return carriage)
        ircmsg = ircmsg.lstrip(":")             # Remove first colon. Useless, waste of space >_<
        print("%s: %s" % (i, ircmsg))                           # print received data

        ircparts = re.split("\s", ircmsg, 3)

        if ircparts[0] == '':
            continue

        if ircraw.find("433 * %s :Nickname is already in use." % cfg.nick()) != -1:
            ircsock.send("NICK " + (cfg.nick() + "|" + str(randint(0, 256))) + "\n")

        if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
            ping()

        if ircmsg.find("NOTICE %s :This nickname is registered" % cfg.nick()) != -1:
            ircsock.send("PRIVMSG NickServ :identify %s\r\n" % cfg.nspass())

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(cfg.chan())

        if ircparts[1] != '' and ircparts[1] == "PRIVMSG":
            tmpusernick = ircparts[0].split('!')[0]
            channel = ircparts[2]
            if channel[0] != '#':
                channel = tmpusernick
            message = ircparts[3].lstrip(":")

            commands(tmpusernick, message, channel)
            triggers(tmpusernick, message, channel)

        i += 1

    # See ya!
    ircsock.send("QUIT %s\r\n" % cfg.quitmsg())
    ircsock.close()
