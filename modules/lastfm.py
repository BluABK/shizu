__author__ = 'BluABK <abk@blucoders.net'

# This module requires pylast to be installed https://github.com/pylast/pylast
import ConfigParser
import os
import re
import cgi

import colours as clr


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

# if module_exists("pylast") is True:
#    import pylast

if module_exists("modules.forklast") is True:
    import modules.forklast as pylast
else:
    print "IMPORT ERROR: Unable to import pylast, expect issues!"

my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.red


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
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
                return None

    def add_alias(self, nick, user):
        if self.config.has_option('lastfm-alias', nick) is False:
            try:
                config = Config.config
                config.set('lastfm-alias', nick, user)
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                return "Alias added"
            except:
                return "Unable to open configuration"
        else:
            return "Alias already exists"

    def list_alias(self):
        if self.config.has_section('lastfm-alias') is True:
            return str(self.config.items('lastfm-alias'))
        else:
            return "Wha! The section has left the building T_T"


cfg = Config()
commandsavail_short = "np, npt"
commandsavail = "imaginary, recent*"
network = pylast.LastFMNetwork(api_key=cfg.api_key(), api_secret=cfg.api_secret(),
                               username=cfg.username(), password_hash=cfg.password_hash())


def test_playing(user):
    try:
        return network.get_user(user).get_now_playing()
    except pylast.WSError:
        print ('%s[%s\t test_playing()]%s: network.get_user(%s).get_now_playing(): No such user' %
               (my_colour, my_name, clr.off, user))
        return "No user with that name was found"


def format_basic(li):
    f_li = list()
    for track in li:
        unicode_track = unicode(str(track.track), 'utf8')
        f_li.append((track.playback_date + "\t" + unicode_track).encode('utf-8'))
        # Debug print
        print (track.playback_date + "\t" + unicode_track).encode('utf-8')
    return f_li


def strip_biojunk(string):
    newstring = ""
    for char in string:
        # 512 bytes is more than enough of a summary (amount takes sendmsg() into account
        if newstring.__sizeof__() > 493:
            newstring += "..."
            break
        # "read more..." and other junk usually happens after a few newlines
        if char == "\n":
            newstring += "..."
            break
        else:
            newstring += char
    return newstring


def strip_html(data):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    # Remove well-formed tags, fixing mistakes by legitimate users
    no_tags = tag_re.sub('', data)

    # Clean up anything else by escaping
    return cgi.escape(no_tags)


def now_playing(user):
    try:
        u = cfg.test_alias(user)
        if u is None:
            print ('%s[%s\t now_playing()]%s: No local alias found for %s, trying online database' %
                   (my_colour, my_name, clr.off, user))
            u = user

        try:
            # These are not the hacks you are looking for, move along
            base = str(network.get_user(u).get_now_playing())
            print "DEBUG: base = %s" % base
            artist = base.split(' - ', 1)[0]
            title = base.split(' - ', 1)[1]
            album = str(network.get_album(artist, title).get_the_sodding_name())
            print "DEBUG: album mayhaps: %s" % album
            # album = str(network.get_album(artist, title))
            # album = str(network.get_album(artist, title).get_url())
            # album = str(network.search_for_track(artist, title))
            # print "DEBUG album maybe: %s" % album
            # album = "THIS IS TOTALLY NOT A FILLER FOR TESTING PURPOSES OR ANYTHING, B-BAKA!"
            np = artist + " - " + album + " - " + title
            return np
            #return network.get_user(u).get_now_playing()
        except IndexError:
            print ('%s[%s\t now_playing()]%s: Index out of range (timeout) for %s' % (my_colour, my_name, clr.off, u))
            return "timeout"
    except pylast.WSError:
        print ('%s[%s\t now_playing()]%s: User %s DERPED' % (my_colour, my_name, clr.off, user))
        return None


def recently_played(user, num):
    try:
        u = cfg.test_alias(user)
        if u is None:
            print ('%s[%s\t now_playing()]%s: User Alias was None, Using argument \'%s\' instead' %
                   (my_colour, my_name, clr.off, user))
            u = user
        rplist = network.get_user(u).get_recent_tracks(limit=num)
#    except pylast.WSError.details == "Rate limit exceeded":
#        return "Rate limit exceeded o0"
    except pylast.WSError:
        # err = "No user with that name was found"
        return None
    print ('%s[%s\t now_playing()]%s: recently played list:' % (my_colour, my_name, clr.off))
    print my_colour
    format_basic(rplist)
    print clr.off
    return format_basic(rplist)


def artist_bio(name):
    try:
        data = network.get_artist(name).get_bio_summary()
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    except pylast.WSError:
        data = "There was an error or some shit, happy now SpyTec? (Translation: General Error)"
        return data
    data = strip_html(data).encode('utf-8')
    try:
        data = strip_biojunk(data)
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    print data
    return data


def add_alias(nick, user):
    return cfg.add_alias(nick, user)


# def del_alias(nick, user):


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    cmdlist.append("Available subcommands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
