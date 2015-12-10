from collections import deque
import os
import ConfigParser


# TODO: Fix and re-enable colours && Make colours.py optional
import colours as clr

__author__ = 'bluabk'

my_name = str(os.path.basename(__file__).split('.', 1)[0])
root_dir = os.path.split(os.path.dirname(__file__))[0]


def communicate(msg, module=None, facility=None, retval=False, truncate="", trunc_size=54, indent=25):
    """
    A syslog-esque print of messages from modules
    :param msg:
    :param module:
    :param facility:
    :param retval:
    :param truncate:
    :param trunc_size:
    :param indent:
    :return:
    """
    identifier = spacing = None
    if truncate is not "":
        if truncate == "mid":
            msg = msg[0:trunc_size/2] + ".." + msg[(len(msg)-trunc_size/2):-1]
    if module is not None:
        if facility is not None:
            identifier = "[%s.%s]:" % (module, facility)
        else:
            identifier = "[%s]:" % module
        spacing = " " * (indent-len(identifier))
    if retval:
        return "%s%s%s" % (identifier, spacing, msg)
    else:
        print "%s%s%s" % (identifier, spacing, msg)


class Config:
    """
    Shizu configuration handler
    """
    default = ConfigParser.RawConfigParser()

    def __init__(self):
        facility = 'config'
        communicate("Initiating config...", my_name, facility=facility)
        self.default.read('config.ini')

    def server(self):
        if self.default.has_option('irc', 'server'):
            return str(self.default.get('irc', 'server'))

    def spass(self):
        if self.default.has_option('irc', 'password'):
            return str(self.default.get('irc', 'password'))

    def port(self):
        if self.default.has_option('irc', 'port'):
            return int(self.default.get('irc', 'port'))

    def chan(self):
        if self.default.has_option('irc', 'channel'):
            return str(self.default.get('irc', 'channel'))

    def nick(self):
        if self.default.has_option('irc', 'nickname'):
            return str(self.default.get('irc', 'nickname'))

    def realname(self):
        if self.default.has_option('irc', 'real name'):
            return str(self.default.get('irc', 'real name'))

    def has_oper(self):
        try:
            if self.default.has_option('irc', 'oper name') and self.default.has_option('irc', 'oper password'):
                if self.oper_pass() != "" and self.oper_name() != "":
                    return True
            else:
                return False
        except:
            return False

    def oper_name(self):
        if self.default.has_option('irc', 'oper name'):
            return str(self.default.get('irc', 'oper name'))

    def oper_pass(self):
        if self.default.has_option('irc', 'oper password'):
            return str(self.default.get('irc', 'oper password'))

    def cmdsym(self):
        if self.default.has_option('irc', 'cmdsymbol'):
            return str(self.default.get('irc', 'cmdsymbol'))

    def quitmsg(self):
        if self.default.has_option('irc', 'quit-message'):
            return str(self.default.get('irc', 'quit-message'))

    def quitpro(self):
        if self.default.has_option('irc', 'quit-protection'):
            return str(self.default.get('irc', 'quit-protection'))

    def proxy_nicks(self):
        if self.default.has_option('irc', 'proxy-users'):
            return_dbg = self.default.get('irc', 'proxy-users')
            return return_dbg

    def su(self):
        if self.default.has_option('users', 'superusers'):
            return str(self.default.get('users', 'superusers'))

    def nspass(self):
        if self.default.has_option('nickserv', 'password'):
            return str(self.default.get('nickserv', 'password'))

cfg = Config()
clr_selection = deque(clr.pool())
my_nickname = cfg.nick()

# TODO: Needs more work, send in path to conf and read() maybe?
def cfg_has_sect(module, config, section):
    """
    ConfigParser has_section wrapper which prints info to shell if it fails
    :param module:
    :param config:
    :param section:
    :return:
    """
    if config.has_section(section):
        return True
    else:
        communicate("ERROR: Configuration file is missing section '%s'" % section, module, facility='config')
        return False

# TODO: Needs more work, send in path to conf and read() maybe?
def cfg_has_opt(module, config, section, option):
    """
    ConfigParser has_option wrapper which prints info to shell if it fails
    :param module:
    :param config:
    :param section:
    :return:
    """
    if config.has_section(section):
        return True
    else:
        communicate("WARNING: Configuration file is missing option '%s' in section '%s'"
                    % (option, section), module, facility='config')
        return False


def sendmsg(msg, chan, ircsock):
    try:
        if isinstance(msg, basestring):
            try:
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, msg))
            except ValueError:
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Oi! That's not a string OwO Are you trying to kill me?!"))
                ircsock.send("PRIVMSG %s :%s\r\n" % (chan, "Hey... Are you trying to kill me?!"))
        else:
            # Don't check, errors from here are raised
            for item in msg:
                sendmsg(item, chan, ircsock)
    except TypeError:
        ircsock.send("PRIVMSG %s :A TypeError occurred, that's annoying..\r\n" % chan)


def debug(msg, ircsock):
    ircsock.send("PRIVMSG %s :DEBUG: %s\r\n" % (cfg.chan(), msg))

