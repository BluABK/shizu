__author__ = 'bluabk'

# Import necessary modules
import socket           # A rather useful network tool
import time             # For time-based greeting functionality
import re               # RegEx for string work.

# Project-specific modules
import ConfigParser
import samba    # for server-specific samba functionality

# Some basic and/or static configuration
run = True

# Some varibles
ircbacklog = list()
maxbacklog = 10

def is_number(s):
     try:
        int(s)
        return True
     except ValueError:
        return False

class BotInfo:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read("config.ini")

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

bI = BotInfo()


def commands(usernick, msg):
    global bI, re
    # General commands
    if msg.find(bI.cmdsym() + "awesome") != -1:
        sendmsg("Everything is awesome!")
    elif msg.find(bI.cmdsym() + "nyaa") != -1:
        nyaa()
    elif msg.find(bI.cmdsym() + "replay") != -1:
        matches = re.search(r"replay (\d+)",msg)
        try:
            arg = matches.group(1)
            if is_number(arg) and int(arg) <= maxbacklog:
                replay(int(arg))
            else:
                replay(0)
        except AttributeError:
            replay(0)
    elif msg.find(bI.cmdsym() + "quit%s" % bI.quitpro()) != -1:
        ircquit()

    # Help calls
    if ircmsg.find(bI.cmdsym() + "help") != -1:
        sendmsg(usernick + ": Yeah, no...")
        sendmsg("Syntax: %scommand help arg1..argN" % bI.cmdsym())
        sendmsg("Available commands: awesome, nyaa, samba* (* command contains sub-commands)")

    # Module: samba
    if msg.find(bI.cmdsym() + "samba") != -1:
        if msg.find(bI.cmdsym() + "samba logins") != -1:
            matches = re.search(r"samba logins (\w+)", msg)
            try:
                for item in xrange(len(samba.getlogins())):
                    if samba.getlogins()[item].name == matches.group(1):
                        sendmsg("%s@%s        [ID: %s]" % (samba.getlogins()[item].name, samba.getlogins()[item].host, samba.getlogins()[item].uid))
            except AttributeError:
                    for item in xrange(len(samba.getlogins())):
                        sendmsg("%s@%s        [ID: %s]" % (samba.getlogins()[item].name, samba.getlogins()[item].host, samba.getlogins()[item].uid))
        elif msg.find(bI.cmdsym() + "samba" or bI.cmdsym() + "samba help") != -1:
            for item in xrange(len(samba.help())):
                sendmsg(str(samba.help()[item]))


def triggers(usernick, msg, raw):
    global bI
    if raw.find(":Hello " + bI.nick()) != -1:  # If someone greets me, I will greet back.
        greeter = ircmsg.strip(":").split("!")[0]
        sendmsg((getgreeting(greeter)))
    elif msg.find((":hi " or ":Hi " or ":ohi ") + usernick) != -1:  # If someone greets me, I will greet back.
        sendmsg("H-h...Hi there")


def ping():
    ircsock.send("PONG :Pong\n")
    debug("Ping Pong bitchez!")


def sendmsg(msg):
    global bI
    ircsock.send("PRIVMSG %s :%s\r\n" % (bI.chan(), msg))


def debug(msg):
    global bI
    ircsock.send("PRIVMSG %s :DEBUG: %s\r\n" % (bI.chan(), msg))


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
    ircsock.connect((bI.server(), bI.port()))
    #if server_pass != "" {
    #    ircsock.send("PASS " + server_pass + "\n")
    #}

    # Register with the server
    ircsock.send("USER " + bI.nick() + " " + bI.nick() + " " + bI.nick() + " :Nibiiro Shizuka\n")
    ircsock.send("NICK " + bI.nick() + "\n")

    while run:
        ircraw = ircsock.recv(512)             # Receive data from the server
        if len(ircbacklog) > maxbacklog:
            del ircbacklog[-1]                 # Remove oldest entry
        ircbacklog.insert(0, ircraw)
        ircmsg = ircraw.strip("\n\r")           # Remove protocol junk (linebreaks and return carriage)
        ircmsg = ircmsg.lstrip(":")             # Remove first colon. Useless, waste of space >_<
        print(ircmsg)                           # print received data

        ircparts = re.split("\s", ircmsg, 4)

        if ircparts[0] == "PING":  # Gotta pong that ping...pong..<vicious cycle>
            ping()

        if ircmsg.find("NOTICE %s :This nickname is registered" % bI.nick()) != -1:
            ircsock.send("PRIVMSG NickServ :identify %s\r\n" % bI.nspass())

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(bI.chan())

        if ircmsg.find(' PRIVMSG ') != -1:
            tmpusernick = ircmsg.split('!')[0][1:]
        #    chan = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
            commands(tmpusernick, ircmsg)
            triggers(tmpusernick, ircmsg, ircraw)

    # See ya!
    ircsock.send("QUIT %s\r\n" % bI.quitmsg())
    ircsock.close()
