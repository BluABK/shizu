# Imports
import ConfigParser
import os
from subprocess import check_output, CalledProcessError

import colours as clr

__author__ = 'BluABK <abk@blucoders.net'

# Variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = ""
commandsavail = "trigger"
commandsavail_short = "ytt"


# Classes


class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read('config.ini')

    def sample(self):
        return str(self.config.get('sample', 'sampleitem'))


cfg = Config()


# Functions
def get_title(url):
    try:
        return check_output("youtube-dl --get-title %s" % url, shell=True).strip('\n')
    except (OSError, CalledProcessError) as e:
        return e.message


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
