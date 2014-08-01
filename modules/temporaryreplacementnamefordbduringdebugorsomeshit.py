__author__ = 'BluABK <abk@blucoders.net'

# TODO: Implement directory and file index (probably via server-side mlocate db)
# TODO: Implement search/lookup for aforementioned index
# TODO: Implement "new files" func (13:37 shizu > New file: tv-series/TUTVS/The.Ultimate.TV-Series.4K.FLAC-iNSANE.mkv)

# This is a module specification, which contains everything you need to get started on writing a module.

# Imports
import ConfigParser

# Variables
commandsavail = "search, update, locations, erase"


# Classes

class db:
    def __init__(self):
        print "dummy class"

class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read('../config.ini')

    def sample(self):
        return str(self.config.get('db', 'file'))

cfg = Config()

# Functions


def help():
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cfg.cmdsym())
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist