# Imports
import ConfigParser
import os
from subprocess import check_output, CalledProcessError
import re

import colours as clr

__author__ = 'BluABK <abk@blucoders.net'

# TODO: Fix fancy (ref: TODO in colours.py)

# Variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = ""
commandsavail = "trigger"
commandsavail_short = "ytt"
youtube_url = ""
ytt_trigger = True


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


cfg = Config()


# Functions
def get_title(keep=False):
    """
    Grabs title of a YouTube video
    :return:
    """
    if keep:
        url = get_url()
    else:
        url = pop_url()
    try:
        return check_output("youtube-dl --get-title %s" % url, shell=True).strip('\n')
    except (OSError, CalledProcessError) as e:
        return e.message


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
        if re.search('(http[s]?://)?(www.)?(youtube.com|youtu.?be)/+', item):
            print "YouTube: current = %s" % item
            # TODO: add_url(item)
            set_url(item)


def printable_title(fancy=True):
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
    return "%s: %s" % (name, get_title())


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
