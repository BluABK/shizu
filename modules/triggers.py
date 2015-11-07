import re
import time
import os
import ConfigParser


# TODO: Make colours.py optional
import colours as clr
from core import communicate, cfg_has_sect, cfg_has_opt

__author__ = 'bluabk'

# PREFACE
# Global vars
my_name = str(os.path.basename(__file__).split('.', 1)[0])
my_colour = clr.white
facility = 'root'


class Config:
    """
    Shizu configuration handler
    """
    default = ConfigParser.RawConfigParser()

    def __init__(self):
        self.facility = 'config'
        communicate("Initiating config...", my_name, facility=facility)
        self.default.read('config.ini')

    if cfg_has_sect(my_name, default, 'triggers'):
        def triggers_words(self):
            if cfg_has_opt(my_name, self.default, 'triggers', 'words'):
                return str(self.default.get('triggers', 'words'))

        def triggers_badwords(self):
            if cfg_has_opt(my_name, self.default, 'triggers', 'badwords'):
                return str(self.default.get('triggers', 'badwords'))

        def triggers_ignorednicks(self):
            if cfg_has_opt(my_name, self.default, 'triggers', 'ignored-nicks'):
                return str(self.default.get('triggers', 'ignored-nicks'))


def getgreeting(greeter, ircsock):
    t = int(time.strftime("%H"))

    if t >= 17 or t < 4:
        greeting = "Konbanwa"
    elif t >= 12:
        greeting = "Konnichiwa"
    elif t >= 4:
        greeting = "Ohayou gozaimasu"
    elif t <= -1:
        debug("Negative time returned", ircsock)
        greeting = "ohi"
    else:
        debug("Time returned had no valid integer value.", ircsock)
        greeting = "ohi"

    return "%s %s~" % (greeting, greeter)


def triggers(usernick, msg, chan, ircsock):
    greet_pat = re.compile((cfg.triggers_words() + " "), flags=re.IGNORECASE)
    greet_match = re.match(greet_pat, msg)
    nick_match = False
    # TODO: HACK: Actually regex match against msg having exactly triggers_words() + cfg.nick()
    for s in msg.split(" "):
        if s == cfg.nick():
            nick_match = True

    """Greeting"""
    try:
        # if matches.group(0) != "":  # If someone greets me, I will greet back.
        if greet_match and nick_match:
            sendmsg((getgreeting(usernick, ircsock)), chan, ircsock)
    except AttributeError:
        return

    """YouTube Title"""
    if module_exists("modules.youtube"):
        if youtube.get_url() is not None and youtube.get_trigger() is True:
            sendmsg(youtube.printable_title(fancy=False), chan, ircsock)