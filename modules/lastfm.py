__author__ = 'BluABK <abk@blucoders.net'

# This module requires pylast to be installed https://github.com/pylast/pylast
import pylast
import ConfigParser
import os

class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read(os.getcwd() + '/' + "config.ini")

    def loadconfig(self):
        configloc = os.getcwd() + '/' + "config.ini"
        print(configloc)
        self.config.read(configloc)
        return True

    def api_key(self):
        return str(self.config.get('lastfm', 'api-key'))

    def api_secret(self):
        return str(self.config.get('lastfm', 'api-secret'))

    def username(self):
        return str(self.config.get('lastfm', 'username'))

    def password(self):
        return str(self.config.get('lastfm', 'password'))

    def password_hash(self):
        return str(self.config.get('lastfm', 'password_hash'))

    def test_alias(self, user):
        if str(self.config.get('lastfm', 'username')) == user:
            return str(self.config.get('lastfm', 'username'))
        else:
            try:
                return str(self.config.get('lastfm-alias', user))
            except ConfigParser.NoOptionError:
                return "No such user"

cfg = Config()
commandsavail_short = "np, npt"
commandsavail = "imaginary"
network = pylast.LastFMNetwork(api_key=cfg.api_key(), api_secret=cfg.api_secret(),
                               username=cfg.username(), password_hash=cfg.password_hash())


def imaginary():
    return "Imagine that!"


def test_playing(user):
    try:
        return network.get_user(user).get_now_playing()
    except pylast.WSError:
        return "No user with that name was found"


def now_playing(user):
    try:
        return network.get_user(user).get_now_playing()
    except pylast.WSError:
        err = "No user with that name was found"
        u = cfg.test_alias(user)
        if u == "No such user":
            return err
        else:
            return network.get_user(u).get_now_playing()


def recently_played(user, num):
    try:
        return network.get_user(user).get_recent_tracks(limit=num)
    except:
        return "recently_played() failure"


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    cmdlist.append("Syntax: %slastfm help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist