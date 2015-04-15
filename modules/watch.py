__author__ = 'BluABK'

# Example: loops monitoring events forever.
#
import ConfigParser
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
            path = ""
            dir_l = list()
            dir_s = str(self.config.get('watch', 'dir'))
            print "watch: " + str(self.config.get('watch', 'dir'))
            for char in dir_s:
                if char == " ":
                    print "watch: Added path: " + path
                    dir_l.append(path)
                    path = ""
                else:
                    path += char
            return dir_l
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


def stop():
#    asyncore.close_all()
    notifier.stop()


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    return cmdlist


wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CREATE  # watched events


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print event.name
        add(event.name)

notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
notifier.start()

wdd = wm.add_watch(cfg.watch(), mask, rec=True, do_glob=True)

#asyncore.loop()