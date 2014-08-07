__author__ = 'BluABK <abk@blucoders.net'

# TODO: Have module-specific commands loaded from the modules themselves, not shizu.py's command()
# TODO: Support multiple IRC channels
# TODO: Support multiple IRC Servers
# TODO: Support SSL
# TODO: Implement command to trigger server-side permission-sentinel.sh - and assign this to a server-side features mod
# TODO: Add try and SomeReasonableExceptionHandler across code

# Global variables
global re
global ircbacklog
global running

# Import necessary modules
import socket           # A rather *useful* network tool
import time             # For time-based greeting functionality
import re               # Regex for the win.
import ConfigParser
import os
from random import randint

# Project-specific modules # TODO: Make module loading dynamic | TODO: Migrate modules to subdir modules/
#import samba            # for server-side samba functionality
#import db               # for server-side file search and lookup

#debug2348435276342 = """


def getmodules():
    mod_dir = "modules/"
    curdir = os.getcwd()
    modlist = os.listdir(mod_dir)
    print(modlist)
    modulelist = []
    os.chdir(mod_dir)
    for mod in modlist:
        print(mod[:-3])
        if mod[:-3] != "__init__":
            modulelist.append(mod[:-3])
    os.chdir(curdir)
    return modulelist

modules = getmodules()
__import__(str(modules))
#"""
ircbacklog = list()
running = True
commandsavail = "awesome, nyaa, help, quit, triggers, replay"
modulesavail = "samba*"

# TODO: NOT-A-TODO/Shortcut: Classes


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

# TODO: NOT-A-TODO/Shortcut: Variables declared by config file
cfg = Config()
maxbacklog = cfg.backlog()

# TODO: NOT-A-TODO/Shortcut: Functions


def ian(s):  # is a number
    try:
        int(s)
        return True
    except ValueError:
        return False


def ping():
    ircsock.send("PONG :Pong\n")


def sendmsg(msg):
    ircsock.send("PRIVMSG %s :%s\r\n" % (cfg.chan(), msg))


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


def replay(lines):
    for i in range(0, lines):
        sendmsg(ircbacklog[i])


def ircquit():
    global running  # TODO: Figure out why this lone global refuse to be defined with the rest at the top
    running = False


def commands(usernick, msg, chan):
    # General commands
    if msg.find(cfg.cmdsym() + "awesome") != -1:
        sendmsg("Everything is awesome!")
    elif msg.find(cfg.cmdsym() + "nyaa") != -1:
        sendmsg("Nyaa~")
    elif msg.find(cfg.cmdsym() + "replay") != -1:
        matches = re.search(r"replay (\d+)", msg)
        try:
            arg = matches.group(1)
            if ian(arg) and int(arg) <= maxbacklog:
                replay(int(arg))
            else:
                replay(0)
        except AttributeError:
            replay(0)
    elif msg.find(cfg.cmdsym() + "say") != -1:
        matches = re.search(r"say (.+)", msg)
        sendmsg(matches.group(1))
    elif msg.find(cfg.cmdsym() + "act") != -1:
        action = re.search(r"act (.+)", msg)
        ircsock.send(u"PRIVMSG %s :\x01ACTION %s\x01\r\n" % (chan, action.group(1)))
    elif msg.find(cfg.cmdsym() + "quit%s" % cfg.quitpro()) != -1:
        ircquit()

    # Help calls
    if ircmsg.find(cfg.cmdsym() + "help") != -1:
        help(ircmsg, usernick)

    # Module: samba
    if msg.find(cfg.cmdsym() + "samba") != -1:
        if msg.find(cfg.cmdsym() + "samba logins") != -1:
            smblogins = samba.getlogins()
            matches = re.search(r"samba logins (\w+)", msg)
            try:
                for item in xrange(len(smblogins)):
                    if smblogins[item].name == matches.group(1):
                        #if excluded user
                        sendmsg("%s@%s        [ID: %s]" % (smblogins[item].name, smblogins[item].host, smblogins[item].uid))
            except AttributeError:
                    for item in xrange(len(smblogins)):
                        sendmsg("%s@%s        [ID: %s]" % (smblogins[item].name, smblogins[item].host, smblogins[item].uid))
        elif msg.find(cfg.cmdsym() + "samba" or cfg.cmdsym() + "samba help") != -1:
            for item in xrange(len(samba.help())):
                sendmsg(str(samba.help()[item]))


def triggers(usernick, msg, chan, raw):
    matches = re.match("(Hello|O?hi|Ohay|Hey) " + cfg.nick(), msg, flags=re.IGNORECASE)
    try:
        if matches.group(0) != "":  # If someone greets me, I will greet back.
            sendmsg((getgreeting(usernick)))
    except AttributeError:
        return


def help(user, msg):
        sendmsg("%s: Syntax: %scommand help arg1..argN" % (user, cfg.cmdsym()))
        sendmsg("Available commands: %s, %s (* command contains sub-commands)" % (commandsavail, modulesavail))

# TODO: NOT-A-TODO/Shortcut: Main()
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

    while running:
        ircraw = ircsock.recv(512)             # Receive data from the server
        if len(ircbacklog) > maxbacklog:
            del ircbacklog[-1]                 # Remove oldest entry
        ircbacklog.insert(0, ircraw)
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

        try:
            if ircparts[1] != '' and ircparts[1] == "PRIVMSG":
                tmpusernick = ircparts[0].split('!')[0]
                channel = ircparts[2]
                if channel[0] != '#':
                    channel = tmpusernick
                message = ircparts[3].lstrip(":")
                commands(tmpusernick, message, channel)
                triggers(tmpusernick, message, channel, ircraw)
        except IndexError:
            sendmsg("channel = ircparts[2] failed (GLHF interacting with the bot at all):")
            sendmsg(IndexError.message)
        i += 1

    # See ya!
    ircsock.send("QUIT %s\r\n" % cfg.quitmsg())
    ircsock.close()
