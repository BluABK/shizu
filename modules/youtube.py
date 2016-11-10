# Imports
import ConfigParser
import os
from subprocess import check_output, CalledProcessError
import re
import colours as clr

__author__ = 'BluABK <abk@blucoders.net'

# TODO: Fix fancy (ref: TODO in colours.py)
# Classes
class Config:  # Mandatory Config class
    """
    Shizu module configuration
    """
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read('config.ini')

    def sample(self):
        return str(self.config.get('sample', 'sampleitem'))


# Functions
def get_title(keep=False):
    """
    Grabs title of a YouTube video
    :return:
    """
    try:
        get_title_curl(keep)
    except (OSError, CalledProcessError):
        try:
            get_title_ytdl(keep)
        except (OSError, CalledProcessError):
            print "Both retrieval methods failed spectacularly!"
            return None


def get_title_ytdl(keep=False):
    """
    Grabs title of a YouTube video using youtube-dl
    :return:
    """
    cmd = None
    if keep:
        url = get_url()
    else:
        url = pop_url()
    try:
        print "youtube.py: retrieving video for url: %s" % url.strip('\n')
        cmd = "youtube-dl --get-title %s" % url.strip('\n')
        out = check_output(cmd, shell=True)
        out = out.rstrip("\r\n")
        return out
    except (OSError, CalledProcessError) as e:
        print cmd
        return None


def get_title_curl(keep=False):
    """
    Grabs title of a YouTube video using curl
    :return:
    """
    cmd = None
    if keep:
        url = str(get_url())
    else:
        url = str(pop_url())
    try:
        print "curl: retrieving video for url: %s" % url.strip('\n')
        # TODO: Make cross compatible with 100% pyregex
        cmd = "curl -s &s | grep '<title>' | head -n 1 | cut -d '>' -f 2 | cut -d '<' -f 1 | sed 's/ - YouTube$//'" \
              % url.strip('\n')
        out = check_output(cmd, shell=True)
        out = out.strip("\r\n")
        return out
    except(OSError, CalledProcessError) as e:
        print cmd
        return None


def set_url(url):
    """
    Sets current url
    :param url:
    :return:
    """
    global youtube_url
    youtube_url = url


def get_url():
    """
    Gets current url
    :return: youtube_url
    """
    return youtube_url


def pop_url():
    """
    Pops current url
    :return: youtube_url
    """
    ret = youtube_url
    set_url(None)
    return ret


def set_trigger(setting=True):
    """
    Sets boolean url listener trigger
    :param setting:
    :return:
    """
    global ytt_trigger
    ytt_trigger = bool(setting)


def get_trigger():
    """
    Returns state of url listener trigger
    :return:
    """
    return ytt_trigger


def toggle_trigger():
    """
    Flips state of url listener trigger True/False
    :return: ytt_trigger (New state of trigger)
    """
    global ytt_trigger
    ytt_trigger = not ytt_trigger
    return ytt_trigger


def parse_url(msg):
    # if re.search(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', msg).group(0):
    for item in msg.split():
        if re.search('(http[s]?://)?(www\.)?(youtube\.com|youtu\.be)/[^ ]+', item):
            print "YouTube: current = %s" % item
            # TODO: add_url(item)
            set_url(item)


def printable_title(chan, irc, fancy=True):
    """
    Returns a string ready for printing
    (does not print on its own)
    :param fancy:
    :return:
    """
    if fancy:
        name = clr.red + "You" + clr.off + clr.white + "Tube" + clr.off
    else:
        name = "YouTube"
    title = get_title()
    if title is not None:
        irc.sendmsg(name+": "+title, chan)


def help(chan, irc):
    """ public """
    return { "ytt" : "", "ytt trigger" : "" }

def commands():
    return { "ytt" : command_ytt }

def command_ytt(nick, chan, cmd, irc):
    # Command mode (see triggers() for trigger mode)
    if len(cmd) >= 1 and cmd[0].lower() == "trigger":
        new_state = toggle_trigger()
        if new_state is True:
            irc.sendmsg("YouTube Title: Print urls as they appear (trigger mode)", chan)
        else:
            irc.sendmsg("YouTube Title: Print urls if asked to (command mode)", chan)
    elif get_url() is not None and get_trigger() is False:
        printable_title(chan, irc, fancy=False)


def listener(nick, chan, msg, irc):
    """ public """
    parse_url(msg)

    if get_url() is not None and get_trigger() is True:
        printable_title(chan, irc, fancy=False)

# Variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = ""
youtube_url = None
ytt_trigger = True

cfg = Config()
