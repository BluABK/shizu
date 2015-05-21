__author__ = 'BluABK'

# Example: loops monitoring events forever.
#
import ConfigParser
import pyinotify


# Variables
commandsavail_short = "" #"enable, disable stopwatch"
commandsavail = "enable, disable, limit"
#watchdir = cfg.watch()
files = list()
files_erased = list()
files_moved = list()
# Classes


class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read('config.ini')

    def watch(self):
        try:
            dir_l = list()
            dir_s = str(self.config.get('watch', 'dir'))
            print "watch: " + str(self.config.get('watch', 'dir'))
            for s in dir_s.split(" "):
                    print "watch: Added path: " + s
                    dir_l.append(s)
            return dir_l
        except:
            print "Config not implemented"

    def chan(self):
        return str(self.config.get('watch', 'chan'))

    def msg(self):
        return str(self.config.get('watch', 'msg'))

    def notify_limit(self):
        return int(self.config.get('watch', 'limit'))

    def set_notify_limit(self, i):
            try:
                config = Config.config
                config.set('watch', 'limit', i)
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                return "limit set"
            except:
                return "Unable to open configuration"

cfg = Config()


# Functions
def add(filename):
    if "New folder" not in filename:
        files.append(filename)


def erase(filename):
    if "New folder" not in filename:
        files.append(filename)


def move(oldfilename, newfilename):
    files_moved.append(oldfilename + " --> " + newfilename)


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


def notify_limit():
    return int(cfg.notify_limit())


def set_notify_limit(i):
    return cfg.set_notify_limit(i)


def msg():
    return cfg.msg()


def stop():
#    asyncore.close_all()
    notifier.stop()


def helpcmd(cmdsym):
    cmdlist = list()
    if len(commandsavail) > 0 or len(commandsavail_short) > 0:
        cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
        if len(commandsavail) > 0:
            cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
        if len(commandsavail_short) > 0:
            cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    else:
        cmdlist.append("That command has no arguments")

    return cmdlist


wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CREATE  # watched events


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "\033[94mwatch.py: New file: %s\033[0m" % event.name
        #add(event.name, 'new')
        add(event.pathname)

    def process_IN_DELETE(self, event):
        print "\033[94mwatch.py: Erased file: %s\033[0m" % event.name
        #add(event.name, 'del')
        erase(event.pathname)

    def process_IN_MOVED_TO(self, event):
        print "\033[94mwatch.py: Moved file: %s\033[0m --> %s\033[0m" % (event.src_pathname, event.pathname)
        #add(event.name, 'del')
        move(event.src_pathname, event.pathname)

notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
notifier.start()

wdd = wm.add_watch(cfg.watch(), mask, rec=True, do_glob=True)

#asyncore.loop()