__author__ = 'bluabk'

# Import necessary modules
import socket           # A rather useful network tool
import time             # For time-based greeting functionality

# Project-specific modules
import config
import samba    # for server-specific samba functionality

# Some basic and/or static configuration
run = True

# Read the rest from file
# TODO: Ditch this bit and make the bot read the config file on-demand (dynamic config)
server = config.config.get('irc', 'server')
server_pass = config.config.get('irc', 'password')
port = config.config.getint('irc', 'port')
chan = config.config.get('irc', 'channel')
nick = config.config.get('irc', 'nickname')
cmdsym = config.config.get('irc', 'cmdsymbol')
quitmsg = config.config.get('irc', 'quit-message')
quitProtection = config.config.get('irc', 'quit-protection')
nickservPass = config.config.get('nickserv', 'password')

# Commands
def commands(nick, chan, msg):
    # syntax: elif msg.find(nick + ": <trigger>") != 1:
    if msg.find(cmdsym + "awesome") != -1:
        ircsock.send("PRIVMSG %s :Everything is awesome!\r\n" % chan)
    elif msg.find(cmdsym + "smblogins") != -1:
    #    ircsock.send("PRIVMSG %s :DEBUG AHEAD:%s@%s\t[ID: %s]\r\n" % (chan, tmpList[0].name, tmpList[0].host, tmpList[0].id))
    #    ircsock.send("PRIVMSG %s: The following users are currently logged in:" % chan)
        for item in xrange(len(samba.getLogins())):
            ircsock.send("PRIVMSG %s :%s@%s        [ID: %s]\r\n" % (chan, samba.getLogins()[item].name, samba.getLogins()[item].host, samba.getLogins()[item].id))
    elif msg.find(cmdsym + "nyaa") != -1:
        nyaa()
    elif msg.find(cmdsym + "quit%s" % quitProtection) != -1:
        quit()
    elif ircmsg.find(cmdsym + "help") != -1:
        ircsock.send("PRIVMSG %s :Syntax incorrect, please rephrase.\r\n" % chan)

def triggers(nick, chan, msg):  # TODO : Doesn't work apparently =/
        if msg.find(":Hello " + nick) != -1:  # If someone greets me, I will greet back.
            ircsock.send("PRIVMSG %s: DEBUG: Greet function triggered" % chan)
            greeter = ircmsg.strip(":").split("!")[0]
            ircsock.send("PRIVMSG %s:%s" % (chan, getGreeting(greeter)))
        elif msg.find((":hi " or ":Hi " or ":ohi ") + nick) != -1:  # If someone greets me, I will greet back.
            ircsock.send("PRIVMSG %s :H-h...Hi there" % chan)

# other functions
def ping():
    ircsock.send("PONG :Pong\n")

def sendmsg(chan, msg): # TODO : implement across code
    ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")

def sendmsg_all(chans, msg):    # TODO : implement across code
    for i in chans:
        ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")

def join(chan):
    ircsock.send("JOIN " + chan + "\n")

def getGreeting(greeter):
    t = int(time.strftime("%H"))

    print("PRIVMSG " + chan + " :" + "DEBUG:  t = " + str(t))
    print("PRIVMSG " + chan + " :" + "DEBUG:  chan = " + chan)
#    print("greeting = " + greeting)
    print("PRIVMSG " + chan + " :" + "DEBUG:  greeter = " + str(greeter))

    if t >= 17:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    else:
        greeting = "ohi dur"

    return "%s %s~" % (greeting,  greeter)

def nyaa():
    ircsock.send("PRIVMSG " + chan + " :Nyaa~\n")

def quit():
    global run
    run = False

if __name__ == "__main__":
    # Connect to the the server
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((server, port))
    #if server_pass != "" {
    #    ircsock.send("PASS " + server_pass + "\n")
    #}

    # Register with the server
    ircsock.send("USER " + nick + " " + nick + " " + nick + " :Nibiiro Shizuka\n")
    ircsock.send("NICK " + nick + "\n")

    while run:
        ircmsg = ircsock.recv(2048)             # Receive data from the server
        ircmsg = ircmsg.strip("\n\r")           # Remove protocol junk (linebreaks and return carriage)
        print(ircmsg)                           # print received data

        if ircmsg.find("PING :") != -1:  # Gotta pong that ping...pong..<vicious cycle>
            ping()

        if ircmsg.find("NOTICE %s :This nickname is registered" % nick) != -1:
            ircsock.send("PRIVMSG NickServ :identify %s\r\n" % nickservPass)

        if ircmsg.find("NOTICE Auth :Welcome") != -1:
            join(chan)

        if ircmsg.find(' PRIVMSG ') != -1:
            nick = ircmsg.split('!')[0][1:]
            chan = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
            commands(nick, chan, ircmsg)
            triggers(nick, chan, ircmsg)

# See ya!
ircsock.send("QUIT %s\r\n" % quitmsg)
ircsock.close()