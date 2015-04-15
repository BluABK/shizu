__author__ = 'BluABK'

# Example: loops monitoring events forever.
#
import ConfigParser
import asyncore
import pyinotify


# Variables
commandsavail_short = "watch, stopwatch"
#commandsavail = "clear, add"
#watchdir = cfg.watch()
files = list()
# Classes


class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read('config.ini')

    def watch(self):
        try:
            return str(self.config.get('watch', 'dir'))
        except:
            print "Config not implemented"

    def chan(self):
        return str(self.config.get('watch', 'chan'))

    def msg(self):
        return str(self.config.get('watch', 'msg'))

cfg = Config()


# Functions
def add(filename):
    files.append(filename)


def check():
    if len(files) > 0:
        return True
    else:
        return False


def get():
    return files


def clear():
    del files[:]


def notify_chan():
    return cfg.chan()


def msg():
    return cfg.msg()


#def stop():
#    asyncore.close_all()


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    return cmdlist


wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CREATE  # watched events


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        add("New episode added: %s" % event.pathname)

notifier = pyinotify.AsyncNotifier(wm, EventHandler())
wdd = wm.add_watch(cfg.watch(), mask, rec=True)

asyncore.loop()