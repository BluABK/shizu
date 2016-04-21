import ConfigParser
import os
import colours as clr
import pyinotify

__author__ = 'BluABK'

# Classes
class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read('config.ini')

    def watch(self):
        # try:
        dir_l = list()
        dir_s = str(self.config.get('watch', 'dir'))
        print "watch: " + str(self.config.get('watch', 'dir'))
        for s in dir_s.split(" "):
            print "watch: Added path: " + s
            dir_l.append(s)
        return dir_l
        # except:
        #    print "Config not implemented"

    def chan(self):
        return str(self.config.get('watch', 'chan'))

    def msg_add(self):
        return str(self.config.get('watch', 'msg_add'))

    def msg_del(self):
        return str(self.config.get('watch', 'msg_del'))

    def msg_mov(self):
        return str(self.config.get('watch', 'msg_mov'))

    def notify_limit(self):
        return int(self.config.get('watch', 'limit'))

    def set_notify_limit(self, i):
        try:
            self.config.read('config.ini')
            self.config.set('watch', 'limit', i)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            return "limit set"
        except:
            return "Unable to open configuration"


# Functions
def add(filename):
    if "New folder" not in filename:
        files.append(filename)


def erase(filename):
    if "New folder" not in filename:
        files_erased.append(filename)


def move(oldfilename, newfilename):
    files_moved_src.append(oldfilename)
    files_moved_dst.append(newfilename)

    # lame ass hack
    files_moved.append(oldfilename + " " + cfg.msg_mov() + " " + newfilename)


def check_moved():
    if len(files_moved_src) > 0 and files_moved_dst > 0:
        return True
    else:
        return False


def check_erased():
    if len(files_erased) > 0:
        return True
    else:
        return False


def check_added():
    if len(files) > 0:
        return True
    else:
        return False


def check_all():
    if len(files) > 0 and len(files_moved_src) > 0 and len(files_moved_dst) > 0 and len(files_erased) > 0:
        return True
    else:
        return False


def get_added():
    return files


def get_erased():
    return files_erased


def get_moved():
    # return files_moved_src, files_moved_dst
    return files_moved


def get_moved_src():
    return files_moved_src


def get_moved_dst():
    return files_moved_src


def clear_moved():
    del files_moved[:]


def clear_erased():
    del files_erased[:]


def clear_added():
    del files[:]


def clear_all():
    del files[:]
    del files_erased[:]
    del files_moved_src[:]
    del files_moved_dst[:]
    del files_moved[:]


def notify_chan():
    return cfg.chan()


def notify_limit():
    return int(cfg.notify_limit())


def set_notify_limit(i):
    return cfg.set_notify_limit(i)



class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "\033[94mwatch.py: New file: %s\033[0m" % event.name
        # add(event.name, 'new')
        add(event.pathname)

    def process_IN_DELETE(self, event):
        print "\033[94mwatch.py: Erased file: %s\033[0m" % event.name
        # add(event.name, 'del')
        erase(event.pathname)

    def process_IN_MOVED_TO(self, event):
        print "\033[94mwatch.py: Moved file: %s\033[0m --> %s\033[0m" % (event.src_pathname, event.pathname)
        # add(event.name, 'del')
        move(event.src_pathname, event.pathname)


def start():
    """ public """
    global wdd
    notifier.start()

    mask_add = pyinotify.IN_CREATE
    mask_mov = pyinotify.IN_MOVED_TO
    mask_del = pyinotify.IN_DELETE
    mask = mask_add | mask_del
    wdd = wm.add_watch(cfg.watch(), mask, rec=True, auto_add=True, do_glob=True)
    # wdd_add = wm.add_watch(cfg.watch(), mask_add, rec=True, do_glob=True)
    # wdd_mov = wm.add_watch(cfg.watch(), mask_mov, rec=True, do_glob=True)
    # wdd_del = wm.add_watch(cfg.watch(), mask_del, rec=True, do_glob=True)
    # asyncore.loop()


def shutdown():
    """ public """
    for k,i in wdd.iteritems():
        wm.del_watch(i)
    notifier.stop()

def help(nick, chan):
    """ public """
    return {
            "watch enable": "",
            "watch disable": "",
            "watch limit": "<num>"
    }

def commands():
    """ public """

    return { "watch" : command_watch }

def command_watch(nick, chan, cmd, irc):
    if len(cmd) < 1:
        return
    cmd[0] = cmd[0].lower()
    if cmd[0] == "enable":
        watch_enabled = True
        irc.sendmsg("Watch notifications enabled.", chan)

    elif cmd[0] == "disable":
        watch_enabled = False
        irc.sendmsg("Watch notifications disabled.", chan)

    elif cmd[0] == "limit" and len(cmd) >= 2:
        print "watch: Setting watchlimit to %s" % cmd[1]
        watch.set_notify_limit(cmd[1])
        irc.sendmsg("Watch notifications limit set to %s" % cmd[1], chan)

def watch_notify(files, chan, msg, irc):
    for item in files:
        irc.sendmsg("%s %s" % (msg, item), chan)


def watch_notify_moved(files, chan, irc):
    # index = 0
    # strings = list()
    # for li in files:
    # for index in xrange(li[0]):

    # lame ass hack
    for item in files:
        irc.sendmsg(item, chan)

def ping(irc):
    """ public """
    # TODO these three blocks are similar enough that they can be combined somehow
    if check_added():
        if watch_enabled:
            if len(get_added()) <= notify_limit():
                watch_notify(get_added(), notify_chan(), cfg.msg_add(), irc)
                for test in get_added():
                    print ("\033[94mNotified: %s\033[0m" % test)
            else:
                cap_list = list()
                for item in get_added()[0:(notify_limit())]:
                    cap_list.append(item)

                cap_list[notify_limit() - 1] += \
                    " ... and " + str(len(get_added()) - notify_limit()) + " more unlisted entries"
                watch_notify(cap_list, notify_chan(), cfg.msg_add(), irc)
        else:
            for test in get_added():
                print ("\033[94mIgnored notify: %s\033[0m" % test)

        clear_added()

    if check_erased():
        if watch_enabled:
            if len(get_erased()) <= notify_limit():
                watch_notify(get_erased(), notify_chan(), cfg.msg_del(), irc)
                print "Debug del sign is %s" % cfg.msg_del()
                for test in get_erased():
                    print ("\033[94mNotified: %s\033[0m" % test)
            else:
                cap_list = list()
                for item in get_erased()[0:(notify_limit())]:
                    cap_list.append(item)

                cap_list[notify_limit() - 1] += \
                    " ... and " + str(len(get_erased()) - notify_limit()) + " more unlisted entries"
                print "Debug2 del sign is %s" % cfg.msg_del()
                watch_notify(cap_list, notify_chan(), cfg.msg_del(), irc)
        else:
            for test in get_erased():
                print ("\033[94mIgnored notify: %s\033[0m" % test)

        clear_erased()

    if check_moved():
        if watch_enabled:
            if len(get_moved()) <= notify_limit():
                watch_notify_moved(get_moved(), notify_chan(), irc)
                for test in get_moved():
                    print ("\033[94mNotified: %s\033[0m" % test)
            else:
                cap_list = list()
                for item in get_moved()[0:(notify_limit())]:
                    cap_list.append(item)

                cap_list[notify_limit() - 1] += \
                    " ... and " + str(len(get_moved()) - notify_limit()) + " more unlisted entries"
                watch_notify(cap_list, notify_chan(), cfg.msg_mov(), irc)

        clear_moved()

watch_enabled = True

my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.blue

cfg = Config()

# watchdir = cfg.watch()
files = list()
files_erased = list()
files_moved = list()
files_moved_src = list()
files_moved_dst = list()


wm = pyinotify.WatchManager()  # Watch Manager
notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
wdd = None

