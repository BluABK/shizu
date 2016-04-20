import ConfigParser
import cgi
import os
import re

import colours as clr

__author__ = 'BluABK <abk@blucoders.net'


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


if module_exists("pylast") is True:
    import pylast

# if module_exists("modules.forklast") is True:
#    import modules.forklast as pylast
else:
    print "This module requires pylast to be installed https://github.com/pylast/pylast"
    print "IMPORT ERROR: Unable to import pylast, expect issues!"

my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.red


class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        """
        Shizu module config class
        :return:
        """
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read(os.getcwd() + '/' + "config.ini")

    def load(self):
        """
        Loads configuration file 'config.ini'
        :return:
        """
        configloc = os.getcwd() + '/' + "config.ini"
        print(configloc)
        self.config.read(configloc)
        return True

    def get_api_key(self):
        """
        Last FM API http://www.last.fm/api
        :return:
        """
        return str(self.config.get('lastfm', 'api-key'))

    def get_api_secret(self):
        """
        Last FM API http://www.last.fm/api
        :return:
        """
        return str(self.config.get('lastfm', 'api-secret'))

    def get_username(self):
        return str(self.config.get('lastfm', 'username'))

    def get_password(self):
        return str(self.config.get('lastfm', 'password'))

    def get_password_hash(self):
        return str(self.config.get('lastfm', 'password_hash'))

    def test_alias(self, user):
        """
        Tests if the supplied user is a local alias
        :param user:
        :return:
        """
        if str(self.config.get('lastfm', 'username')) == user:
            return str(self.config.get('lastfm', 'username'))
        else:
            try:
                return str(self.config.get('lastfm-alias', user))
            except ConfigParser.NoOptionError:
                return None

    def add_alias(self, nick, user):
        """
        Adds a lastfm user alias for a nickname
        :param nick: IRC nickname
        :param user: LastFM Username
        :return:
        """
        if self.config.has_option('lastfm-alias', nick) is False:
            try:
                self.config.read('config.ini')
                self.config.set('lastfm-alias', nick, user)
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                    configfile.close()
                return "Alias added"
            except:
                return "Unable to open configuration"
        else:
            return "Alias already exists"

    def del_alias(self, nick):
        """
        Removes a set nickname alias
        :param nick: IRC Nickname
        :return:
        """
        if self.config.has_option('lastfm-alias', nick) is False:
            try:
                self.config.read('config.ini')
                self.config.remove_option('lastfm-alias', nick)
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                    configfile.close()
                return "Alias added"
            except:
                return "Unable to open configuration"
        else:
            return "Alias already exists"

    def list_alias(self):
        """
        Retrieves a list of all aliases and their associated nicknames
        :return:
        """
        if self.config.has_section('lastfm-alias') is True:
            return str(self.config.items('lastfm-alias'))
        else:
            return "Wha! The section has left the building T_T"


cfg = Config()
commandsavail_short = "np, npt, alias"
commandsavail = "imaginary, recent*, bio, status, alias"
network = pylast.LastFMNetwork(api_key=cfg.get_api_key(), api_secret=cfg.get_api_secret(),
                               username=cfg.get_username(), password_hash=cfg.get_password_hash())


def test_connection():
    """
    Self-test for LastFM connectivity
    :return: Authenticated user or pylast Error object
    """
    # debug = list()
    # debug.append(network.get_user())
    try:
        return network.get_authenticated_user().get_name()
    except pylast.WSError as e:
        return e


def test_playing(user):
    """
    Test if user exists (Saves you from pylast issues)
    :param user:
    :return:
    """
    try:
        return network.get_user(user).get_now_playing()
    except pylast.WSError:
        print ('%s[%s\t test_playing()]%s: network.get_user(%s).get_now_playing(): No such user' %
               (my_colour, my_name, clr.off, user))
        return "No user with that name was found"


def format_basic(li):
    """
    Formats a sequence of pylast PlayedTrack objects
    Format: <date>, <time>      <artist> - <track>
    :param li: PlayedTrack[]
    :return: Formatted list (UTF-8)
    """
    f_li = list()
    for track in li:
        unicode_track = unicode(str(track.track), 'utf8')
        f_li.append((track.playback_date + "\t" + unicode_track).encode('utf-8'))
        # Debug print
        print (track.playback_date + "\t" + unicode_track).encode('utf-8')
    return f_li


def strip_biojunk(string, limit):
    """
    Strips irrelevant formatting from a bio and caps it at 512 bytes length
    :param limit: Max length of string
    :param string: Artist biography summary
    :return: Formatted string
    """
    newstring = ""
    for char in string:
        # 512 bytes is more than enough of a summary (amount takes sendmsg() into account
        if newstring.__sizeof__() > limit - 19:
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
    """
    Strips HTML tags from pylast bio summary data
    :param data: pylast.get_bio_summary(self, language=None)
    :return: Formatted string
    """
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    # Remove well-formed tags, fixing mistakes by legitimate users
    no_tags = tag_re.sub('', data)

    # Clean up anything else by escaping
    return cgi.escape(no_tags)


def now_playing(user):
    """
    Takes a LastFM Username and returns what they're currently scrobbling
    :param user: LastFM Username
    :return: str
    """
    try:
        u = cfg.test_alias(user)
        if u is None:
            print ('%s[%s\t now_playing()]%s: No local alias found for %s, trying online database' %
                   (my_colour, my_name, clr.off, user))
            u = user

        try:
            return network.get_user(u).get_now_playing()
        except IndexError:
            print ('%s[%s\t now_playing()]%s: Index out of range (timeout) for %s' % (my_colour, my_name, clr.off, u))
            return "timeout"
    except pylast.WSError:
        print ('%s[%s\t now_playing()]%s: User %s DERPED' % (my_colour, my_name, clr.off, user))
        return None


def recently_played(user, num):
    """
    Returns a formatted list of scrobbled items for supplied user with supplied length (contents permitting)
    :param user: LastFM Username
    :param num: int
    :return:
    """
    try:
        u = cfg.test_alias(user)
        if u is None:
            print ('%s[%s\t now_playing()]%s: User Alias was None, Using argument \'%s\' instead' %
                   (my_colour, my_name, clr.off, user))
            u = user
        try:
            rplist = network.get_user(u).get_recent_tracks(limit=int(num) + 1)
        except (AttributeError, ValueError) as e:
            return e.message
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


def artist_bio(name, limit=512):
    """
    Returns a formatted artist biography summary string with limited length
    :param limit: Default value: 512
    :param name: Artist name
    :return:
    """
    try:
        data = network.get_artist(name).get_bio_summary()
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    except pylast.WSError as e:
        derp = list()
        derp.append("Oh noes, an exception!")
        derp.append(str(e.message))
        derp.append(str(e.details))
        derp.append(str(e.status))
        for a in e.args:
            derp.append(str(a) + ", ")
        return derp
    data = strip_html(data).encode('utf-8')
    try:
        data = strip_biojunk(data, limit)
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    print data
    return data


def add_alias(nick, user):
    """
    Adds IRC nickname alias for LastFM Username
    :param nick: IRC Nickname
    :param user: LastFM Username
    :return: boolean
    """
    return cfg.add_alias(nick, user)


def del_alias(nick):
    """
    Removes IRC nickname alias for LastFM Username
    :param nick: IRC Nickname
    :return: boolean
    """
    return cfg.del_alias(nick)


def helpcmd(cmdsym):
    """
    Shizu module helper
    :param cmdsym: Command trigger symbol
    :return: Filled in list of available commands
    """
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    cmdlist.append("Available subcommands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
