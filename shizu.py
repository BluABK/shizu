__author__ = 'bluabk'

# Import necessary modules
import socket           # A rather *useful* network tool
import time             # For time-based greeting functionality
import re               # RegEx for string work.
import ConfigParser

# Project-specific modules
import samba            # for server-specific samba functionality


class Config:  # Shizu's config class
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

    def cmdsym(self):
        return str(self.config.get('irc', 'cmdsymbol'))

    def quitmsg(self):
        return str(self.config.get('irc', 'quit-message'))

    def quitpro(self):
        return str(self.config.get('irc', 'quit-protection'))

    def nspass(self):
        return str(self.config.get('nickserv', 'password'))

    def getvar(self, group, name):
        return str(self.config.get(group, name))


# Some basic and/or static configuration
run = True

# Variables
ircbacklog = list()
maxbacklog = 10
cfg = Config()


def ian(s):  # is a number
    try:
        int(s)
        return True
    except ValueError:
        return False


def commands(usernick, msg, chan):
    global cfg, re
    # General commands
    if msg.find(cfg.cmdsym() + "awesome") != -1:
        sendmsg("Everything is awesome!")
    elif msg.find(cfg.cmdsym() + "nyaa") != -1:
        nyaa()
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
        sendmsg(usernick + ": Yeah, no...")
        sendmsg("Syntax: %scommand help arg1..argN" % cfg.cmdsym())
        sendmsg("Available commands: awesome, nyaa, samba* (* command contains sub-commands)")

    # Module: samba
    if msg.find(cfg.cmdsym() + "samba") != -1:
        if msg.find(cfg.cmdsym() + "samba logins") != -1:
            matches = re.search(r"samba logins (\w+)", msg)
            try:
                for item in xrange(len(samba.getlogins())):
                    if samba.getlogins()[item].name == matches.group(1):
                        #if excluded user
                        sendmsg("%s@%s        [ID: %s]" % (samba.getlogins()[item].name, samba.getlogins()[item].host, samba.getlogins()[item].uid))
            except AttributeError:
                    for item in xrange(len(samba.getlogins())):
                        sendmsg("%s@%s        [ID: %s]" % (samba.getlogins()[item].name, samba.getlogins()[item].host, samba.getlogins()[item].uid))
        elif msg.find(cfg.cmdsym() + "samba" or cfg.cmdsym() + "samba help") != -1:
            for item in xrange(len(samba.help())):
                sendmsg(str(samba.help()[item]))


def triggers(usernick, msg, chan, raw):
    global cfg, re
    matches = re.match("(Hello|O?hi|Ohay|Hey) " + cfg.nick(), msg, flags=re.IGNORECASE)
    try:
        if matches.group(0) != "":  # If someone greets me, I will greet back.
            sendmsg((getgreeting(usernick)))
    except AttributeError:
        return


def ping():
    ircsock.send("PONG :Pong\n")


def sendmsg(msg):
    global cfg
    ircsock.send("PRIVMSG %s :%s\r\n" % (cfg.chan(), msg))


def debug(msg):
    global cfg
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
    else:
        greeting = "Time is no longer relative, someone might want to investigate this."

    return "%s %s~" % (greeting,  greeter)


def replay(lines):
    global ircbacklog
    for i in range(0, lines):
        sendmsg(ircbacklog[i])


def nyaa():
    sendmsg("Nyaa~")


def ircquit():
    global run
    run = False

if __name__ == "__main__":
    # Connect to the the server
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((cfg.server(), cfg.port()))
    if cfg.spass() != "":
        ircsock.send("PASS " + cfg.spass() + "\n")

    # Register with the server
    ircsock.send("USER " + cfg.nick() + " " + cfg.nick() + " " + cfg.nick() + " :Nibiiro Shizuka\n")
    ircsock.send("NICK " + cfg.nick() + "\n")

    while run:
        ircraw = ircsock.recv(512)             # Receive data from the server
        if len(ircbacklog) > maxbacklog:
            del ircbacklog[-1]                 # Remove oldest entry
        ircbacklog.insert(0, ircraw)
        ircmsg = ircraw.strip("\n\r")           # Remove protocol junk (linebreaks and return carriage)
        ircmsg = ircmsg.lstrip(":")             # Remove first colon. Useless, waste of space >_<
        print(ircmsg)                           # print received data

        ircparts = re.split("\s", ircmsg, 3)

        if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
            ping()

        if ircmsg.find("NOTICE %s :This nickname is registered" % cfg.nick()) != -1:
            ircsock.send("PRIVMSG NickServ :identify %s\r\n" % cfg.nspass())

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(cfg.chan())

        if ircparts[1] == "PRIVMSG":
            tmpusernick = ircparts[0].split('!')[0]
            chan = ircparts[2]
            if chan[0] != '#':
                chan = tmpusernick
            message = ircparts[3].lstrip(":")
            commands(tmpusernick, message, chan)
            triggers(tmpusernick, message, chan, ircraw)

    # See ya!
    ircsock.send("QUIT %s\r\n" % cfg.quitmsg())
    ircsock.close()
